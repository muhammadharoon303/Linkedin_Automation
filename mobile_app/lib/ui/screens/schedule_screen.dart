import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/app_state.dart';
import '../../core/models/platform_type.dart';
import '../../core/models/scheduled_post.dart';
import '../widgets/post_card.dart';

class ScheduleScreen extends StatefulWidget {
  const ScheduleScreen({super.key});

  @override
  State<ScheduleScreen> createState() => _ScheduleScreenState();
}

class _ScheduleScreenState extends State<ScheduleScreen> {
  SocialPlatform? _selectedPlatformFilter;

  void _showEditScheduleModal(ScheduledPost post) async {
    final appState = Provider.of<AppState>(context, listen: false);

    final pickedDate = await showDatePicker(
      context: context,
      initialDate: post.scheduledDateTime,
      firstDate: DateTime.now().subtract(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );

    if (pickedDate == null || !mounted) return;

    final pickedTime = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(post.scheduledDateTime),
    );

    if (pickedTime == null || !mounted) return;

    final newDateTime = DateTime(
      pickedDate.year,
      pickedDate.month,
      pickedDate.day,
      pickedTime.hour,
      pickedTime.minute,
    );

    await appState.updatePost(
      post.copyWith(scheduledDateTime: newDateTime),
    );

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Post rescheduled successfully!')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final appState = context.watch<AppState>();

    var posts = appState.posts.where((p) => p.status == PostStatus.scheduled).toList();

    if (_selectedPlatformFilter != null) {
      posts = posts.where((p) => p.platform == _selectedPlatformFilter).toList();
    }

    posts.sort((a, b) => a.scheduledDateTime.compareTo(b.scheduledDateTime));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Publishing Schedule'),
      ),
      body: Column(
        children: [
          // Platform Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                FilterChip(
                  label: const Text('All Platforms'),
                  selected: _selectedPlatformFilter == null,
                  onSelected: (_) => setState(() => _selectedPlatformFilter = null),
                ),
                const SizedBox(width: 8),
                ...SocialPlatform.values.map((plat) {
                  final isSelected = _selectedPlatformFilter == plat;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: FilterChip(
                      avatar: Icon(plat.icon, size: 16, color: plat.brandColor),
                      label: Text(plat.displayName),
                      selected: isSelected,
                      onSelected: (_) => setState(() {
                        _selectedPlatformFilter = isSelected ? null : plat;
                      }),
                    ),
                  );
                }),
              ],
            ),
          ),
          const Divider(height: 1),

          Expanded(
            child: posts.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.event_note, size: 48, color: Colors.grey),
                        const SizedBox(height: 12),
                        Text(
                          'No scheduled posts found',
                          style: theme.textTheme.titleMedium,
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Generate a campaign to populate your schedule queue.',
                          style: TextStyle(color: Colors.grey, fontSize: 13),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: posts.length,
                    itemBuilder: (ctx, index) {
                      final post = posts[index];
                      return PostCard(
                        post: post,
                        onTap: () => _showEditScheduleModal(post),
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
