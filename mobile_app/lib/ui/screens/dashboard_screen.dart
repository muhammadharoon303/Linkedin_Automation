import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/app_state.dart';
import '../../core/models/scheduled_post.dart';
import '../widgets/stat_card.dart';
import '../widgets/post_card.dart';
import 'campaign_builder_screen.dart';
import 'projects_screen.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  void _showPostDetailModal(BuildContext context, ScheduledPost post) {
    final theme = Theme.of(context);
    final appState = Provider.of<AppState>(context, listen: false);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: theme.colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.75,
        maxChildSize: 0.95,
        minChildSize: 0.5,
        expand: false,
        builder: (_, scrollController) => SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.outlineVariant,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Icon(post.platform.icon, color: post.platform.brandColor, size: 24),
                  const SizedBox(width: 10),
                  Text(
                    post.platform.displayName,
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: post.platform.brandColor,
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: post.status.color.withAlpha(30),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      post.status.displayName,
                      style: TextStyle(
                        color: post.status.color,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                'Topic: ${post.topic}',
                style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                'Scheduled For: ${post.scheduledDateTime.toString().substring(0, 16)}',
                style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.outline),
              ),
              const Divider(height: 32),
              Text(
                'Post Content:',
                style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest.withAlpha(60),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: theme.colorScheme.outlineVariant.withAlpha(50)),
                ),
                child: SelectableText(
                  post.finalContent,
                  style: theme.textTheme.bodyMedium?.copyWith(height: 1.5),
                ),
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  if (post.status == PostStatus.scheduled) ...[
                    Expanded(
                      child: ElevatedButton.icon(
                        icon: const Icon(Icons.send_rounded),
                        label: const Text('Publish Now'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                        ),
                        onPressed: () {
                          appState.publishPostNow(post.id);
                          Navigator.pop(ctx);
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Post published successfully!')),
                          );
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],
                  Expanded(
                    child: OutlinedButton.icon(
                      icon: const Icon(Icons.delete_outline, color: Colors.red),
                      label: const Text('Delete Post', style: TextStyle(color: Colors.red)),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        side: const BorderSide(color: Colors.red),
                      ),
                      onPressed: () {
                        appState.deletePost(post.id);
                        Navigator.pop(ctx);
                      },
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final appState = context.watch<AppState>();
    final activeProject = appState.activeProject;
    final scheduledPosts = appState.posts
        .where((p) => p.status == PostStatus.scheduled)
        .toList()
      ..sort((a, b) => a.scheduledDateTime.compareTo(b.scheduledDateTime));

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Social AI Studio',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            if (activeProject != null)
              Text(
                activeProject.name,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
          ],
        ),
        actions: [
          // Backend Status Badge
          Container(
            margin: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: appState.backendStatus == 'online'
                  ? Colors.green.withAlpha(30)
                  : Colors.amber.withAlpha(30),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: appState.backendStatus == 'online' ? Colors.green : Colors.amber,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircleAvatar(
                  radius: 4,
                  backgroundColor:
                      appState.backendStatus == 'online' ? Colors.green : Colors.amber,
                ),
                const SizedBox(width: 6),
                Text(
                  appState.backendStatus == 'online' ? 'Ollama Online' : 'Local Mode',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: appState.backendStatus == 'online'
                        ? Colors.green[800]
                        : Colors.amber[900],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => appState.checkBackendHealth(),
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Master Automation Control Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      theme.colorScheme.primaryContainer,
                      theme.colorScheme.surfaceContainerHighest,
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.primary.withAlpha(30),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        appState.autoPostingMasterSwitch
                            ? Icons.auto_awesome
                            : Icons.pause_circle_outline,
                        color: theme.colorScheme.primary,
                        size: 26,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Automatic Posting',
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            appState.autoPostingMasterSwitch
                                ? 'Active: Queued posts publish on schedule'
                                : 'Paused: All scheduled publishing on hold',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Switch.adaptive(
                      value: appState.autoPostingMasterSwitch,
                      onChanged: (val) => appState.toggleAutoPosting(val),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Metrics Grid
              Row(
                children: [
                  Expanded(
                    child: StatCard(
                      title: 'Scheduled',
                      count: '${appState.scheduledCount}',
                      icon: Icons.schedule,
                      color: Colors.blue,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: StatCard(
                      title: 'Published',
                      count: '${appState.publishedCount}',
                      icon: Icons.check_circle_outline,
                      color: Colors.green,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: StatCard(
                      title: 'Campaigns',
                      count: '${appState.campaigns.length}',
                      icon: Icons.campaign_outlined,
                      color: Colors.purple,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: StatCard(
                      title: 'Ref Docs',
                      count: '${activeProject?.documents.length ?? 0}',
                      icon: Icons.description_outlined,
                      color: Colors.teal,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Primary Action Buttons
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      icon: const Icon(Icons.rocket_launch, size: 20),
                      label: const Text(
                        'Create 30-Day Campaign',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: theme.colorScheme.primary,
                        foregroundColor: theme.colorScheme.onPrimary,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const CampaignBuilderScreen(),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      icon: const Icon(Icons.folder_open, size: 18),
                      label: const Text('Manage Docs & Rules'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const ProjectsScreen(),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 28),

              // Active Campaigns Preview
              if (appState.campaigns.isNotEmpty) ...[
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Active Campaigns',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      '${appState.campaigns.length} Total',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.outline,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                ...appState.campaigns.take(2).map((camp) {
                  final campPosts =
                      appState.posts.where((p) => p.campaignId == camp.id).toList();
                  final pubCount =
                      campPosts.where((p) => p.status == PostStatus.published).length;
                  final total = campPosts.isNotEmpty ? campPosts.length : camp.totalPostsCount;
                  final progress = total > 0 ? pubCount / total : 0.0;

                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surface,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: theme.colorScheme.outlineVariant.withAlpha(70),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.calendar_today, size: 16, color: Colors.purple),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                camp.title,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 15,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            ...camp.selectedPlatforms.map(
                              (p) => Padding(
                                padding: const EdgeInsets.only(right: 6),
                                child: Icon(p.icon, size: 16, color: p.brandColor),
                              ),
                            ),
                            const Spacer(),
                            Text(
                              '$pubCount / $total posted',
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: theme.colorScheme.outline,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: progress,
                            minHeight: 6,
                            backgroundColor: theme.colorScheme.surfaceContainerHighest,
                            valueColor: AlwaysStoppedAnimation<Color>(theme.colorScheme.primary),
                          ),
                        ),
                      ],
                    ),
                  );
                }),
                const SizedBox(height: 20),
              ],

              // Upcoming Queue
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Upcoming Queue',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    '${scheduledPosts.length} Queued',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              if (scheduledPosts.isEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 36, horizontal: 16),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest.withAlpha(40),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: theme.colorScheme.outlineVariant.withAlpha(40)),
                  ),
                  child: Column(
                    children: [
                      Icon(Icons.event_available,
                          size: 40, color: theme.colorScheme.outline),
                      const SizedBox(height: 10),
                      Text(
                        'No upcoming posts in queue',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Tap "Create 30-Day Campaign" above to schedule automated posts.',
                        textAlign: TextAlign.center,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                    ],
                  ),
                )
              else
                ...scheduledPosts.take(5).map(
                      (post) => PostCard(
                        post: post,
                        onTap: () => _showPostDetailModal(context, post),
                        onPublishNow: () {
                          appState.publishPostNow(post.id);
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Published post now!')),
                          );
                        },
                        onDelete: () => appState.deletePost(post.id),
                      ),
                    ),
            ],
          ),
        ),
      ),
    );
  }
}
