import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../../providers/app_state.dart';
import '../../core/models/scheduled_post.dart';
import '../widgets/post_card.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final TextEditingController _searchController = TextEditingController();
  PostStatus? _statusFilter;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _showPostDetailModal(BuildContext context, ScheduledPost post) {
    final theme = Theme.of(context);
    final appState = Provider.of<AppState>(context, listen: false);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(post.platform.icon, color: post.platform.brandColor, size: 24),
                const SizedBox(width: 8),
                Text(
                  post.platform.displayName,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const Spacer(),
                Chip(
                  label: Text(post.status.displayName),
                  backgroundColor: post.status.color.withAlpha(30),
                  labelStyle: TextStyle(color: post.status.color, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              post.topic,
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest.withAlpha(50),
                borderRadius: BorderRadius.circular(8),
              ),
              child: SelectableText(post.finalContent),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    icon: const Icon(Icons.copy),
                    label: const Text('Copy Content'),
                    onPressed: () {
                      Clipboard.setData(ClipboardData(text: post.finalContent));
                      Navigator.pop(ctx);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Content copied!')),
                      );
                    },
                  ),
                ),
                const SizedBox(width: 8),
                if (post.status != PostStatus.published)
                  Expanded(
                    child: ElevatedButton.icon(
                      icon: const Icon(Icons.send),
                      label: const Text('Publish Now'),
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                      onPressed: () {
                        appState.publishPostNow(post.id);
                        Navigator.pop(ctx);
                      },
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final appState = context.watch<AppState>();

    var list = appState.posts;

    if (_statusFilter != null) {
      list = list.where((p) => p.status == _statusFilter).toList();
    }

    final query = _searchController.text.trim().toLowerCase();
    if (query.isNotEmpty) {
      list = list
          .where((p) =>
              p.topic.toLowerCase().contains(query) ||
              p.finalContent.toLowerCase().contains(query))
          .toList();
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Posting History'),
      ),
      body: Column(
        children: [
          // Search Field
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search posts by topic or text...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          setState(() {});
                        },
                      )
                    : null,
                contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 16),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onChanged: (_) => setState(() {}),
            ),
          ),

          // Status Filter Tabs
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: Row(
              children: [
                FilterChip(
                  label: Text('All (${appState.posts.length})'),
                  selected: _statusFilter == null,
                  onSelected: (_) => setState(() => _statusFilter = null),
                ),
                const SizedBox(width: 8),
                FilterChip(
                  avatar: const Icon(Icons.check_circle, size: 14, color: Colors.green),
                  label: Text('Published (${appState.publishedCount})'),
                  selected: _statusFilter == PostStatus.published,
                  onSelected: (_) => setState(
                    () => _statusFilter = _statusFilter == PostStatus.published
                        ? null
                        : PostStatus.published,
                  ),
                ),
                const SizedBox(width: 8),
                FilterChip(
                  avatar: const Icon(Icons.schedule, size: 14, color: Colors.blue),
                  label: Text('Scheduled (${appState.scheduledCount})'),
                  selected: _statusFilter == PostStatus.scheduled,
                  onSelected: (_) => setState(
                    () => _statusFilter = _statusFilter == PostStatus.scheduled
                        ? null
                        : PostStatus.scheduled,
                  ),
                ),
                const SizedBox(width: 8),
                FilterChip(
                  avatar: const Icon(Icons.error_outline, size: 14, color: Colors.red),
                  label: Text('Failed (${appState.failedCount})'),
                  selected: _statusFilter == PostStatus.failed,
                  onSelected: (_) => setState(
                    () => _statusFilter =
                        _statusFilter == PostStatus.failed ? null : PostStatus.failed,
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 12),

          // Posts List
          Expanded(
            child: list.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.history, size: 48, color: Colors.grey),
                        const SizedBox(height: 12),
                        Text('No posts found', style: theme.textTheme.titleMedium),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: list.length,
                    itemBuilder: (ctx, idx) {
                      final post = list[idx];
                      return PostCard(
                        post: post,
                        onTap: () => _showPostDetailModal(context, post),
                        onPublishNow: () => appState.publishPostNow(post.id),
                        onDelete: () => appState.deletePost(post.id),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
