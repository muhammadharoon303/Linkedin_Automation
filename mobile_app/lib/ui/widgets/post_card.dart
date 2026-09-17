import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import '../../core/models/scheduled_post.dart';

class PostCard extends StatelessWidget {
  final ScheduledPost post;
  final VoidCallback? onTap;
  final VoidCallback? onPublishNow;
  final VoidCallback? onDelete;

  const PostCard({
    super.key,
    required this.post,
    this.onTap,
    this.onPublishNow,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final platform = post.platform;
    final formattedDate = DateFormat('EEE, MMM d • hh:mm a').format(post.scheduledDateTime);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: theme.colorScheme.outlineVariant.withAlpha(80)),
      ),
      color: theme.colorScheme.surface,
      margin: const EdgeInsets.symmetric(vertical: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header: Platform Badge, Time, and Status
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: platform.brandColor.withAlpha(25),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(platform.icon, size: 15, color: platform.brandColor),
                        const SizedBox(width: 6),
                        Text(
                          platform.displayName,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: platform.brandColor,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: post.status.color.withAlpha(25),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(post.status.icon, size: 12, color: post.status.color),
                        const SizedBox(width: 4),
                        Text(
                          post.status.displayName,
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: post.status.color,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),

              // Topic / Title
              Text(
                post.topic,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 6),

              // Content snippet
              Text(
                post.finalContent,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  height: 1.4,
                ),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),

              // Footer: Scheduled Time & Actions
              Row(
                children: [
                  Icon(Icons.access_time, size: 14, color: theme.colorScheme.outline),
                  const SizedBox(width: 4),
                  Text(
                    formattedDate,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.copy, size: 18),
                    tooltip: 'Copy text',
                    onPressed: () {
                      Clipboard.setData(ClipboardData(text: post.finalContent));
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Copied post content to clipboard!'),
                          duration: Duration(seconds: 2),
                        ),
                      );
                    },
                  ),
                  if (post.status == PostStatus.scheduled && onPublishNow != null)
                    IconButton(
                      icon: const Icon(Icons.send_rounded, size: 18, color: Colors.blue),
                      tooltip: 'Publish Now',
                      onPressed: onPublishNow,
                    ),
                  if (onDelete != null)
                    IconButton(
                      icon: const Icon(Icons.delete_outline, size: 18, color: Colors.redAccent),
                      tooltip: 'Delete',
                      onPressed: onDelete,
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
