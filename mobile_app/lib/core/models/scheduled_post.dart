import 'package:flutter/material.dart';
import 'platform_type.dart';

enum PostStatus {
  draft,
  scheduled,
  published,
  failed;

  String get displayName {
    switch (this) {
      case PostStatus.draft:
        return 'Draft';
      case PostStatus.scheduled:
        return 'Scheduled';
      case PostStatus.published:
        return 'Published';
      case PostStatus.failed:
        return 'Failed';
    }
  }

  Color get color {
    switch (this) {
      case PostStatus.draft:
        return Colors.grey;
      case PostStatus.scheduled:
        return Colors.blue;
      case PostStatus.published:
        return Colors.green;
      case PostStatus.failed:
        return Colors.red;
    }
  }

  IconData get icon {
    switch (this) {
      case PostStatus.draft:
        return Icons.edit_note;
      case PostStatus.scheduled:
        return Icons.schedule;
      case PostStatus.published:
        return Icons.check_circle;
      case PostStatus.failed:
        return Icons.error_outline;
    }
  }
}

/// An individual generated or edited post ready for scheduling or published to a platform.
class ScheduledPost {
  final String id;
  final String projectId;
  final String? campaignId;
  final SocialPlatform platform;
  final String topic;
  final String? hook;
  final String generatedContent;
  final String finalContent;
  final DateTime scheduledDateTime;
  final PostStatus status;
  final bool autoPublish;
  final String? errorMessage;
  final DateTime? publishedAt;
  final DateTime createdAt;

  ScheduledPost({
    required this.id,
    required this.projectId,
    this.campaignId,
    required this.platform,
    required this.topic,
    this.hook,
    required this.generatedContent,
    required this.finalContent,
    required this.scheduledDateTime,
    this.status = PostStatus.scheduled,
    this.autoPublish = true,
    this.errorMessage,
    this.publishedAt,
    required this.createdAt,
  });

  ScheduledPost copyWith({
    String? id,
    String? projectId,
    String? campaignId,
    SocialPlatform? platform,
    String? topic,
    String? hook,
    String? generatedContent,
    String? finalContent,
    DateTime? scheduledDateTime,
    PostStatus? status,
    bool? autoPublish,
    String? errorMessage,
    DateTime? publishedAt,
    DateTime? createdAt,
  }) {
    return ScheduledPost(
      id: id ?? this.id,
      projectId: projectId ?? this.projectId,
      campaignId: campaignId ?? this.campaignId,
      platform: platform ?? this.platform,
      topic: topic ?? this.topic,
      hook: hook ?? this.hook,
      generatedContent: generatedContent ?? this.generatedContent,
      finalContent: finalContent ?? this.finalContent,
      scheduledDateTime: scheduledDateTime ?? this.scheduledDateTime,
      status: status ?? this.status,
      autoPublish: autoPublish ?? this.autoPublish,
      errorMessage: errorMessage ?? this.errorMessage,
      publishedAt: publishedAt ?? this.publishedAt,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'projectId': projectId,
        'campaignId': campaignId,
        'platform': platform.id,
        'topic': topic,
        'hook': hook,
        'generatedContent': generatedContent,
        'finalContent': finalContent,
        'scheduledDateTime': scheduledDateTime.toIso8601String(),
        'status': status.name,
        'autoPublish': autoPublish,
        'errorMessage': errorMessage,
        'publishedAt': publishedAt?.toIso8601String(),
        'createdAt': createdAt.toIso8601String(),
      };

  factory ScheduledPost.fromJson(Map<String, dynamic> json) => ScheduledPost(
        id: json['id'] as String,
        projectId: json['projectId'] as String,
        campaignId: json['campaignId'] as String?,
        platform: SocialPlatform.fromId(json['platform'] as String),
        topic: json['topic'] as String,
        hook: json['hook'] as String?,
        generatedContent: json['generatedContent'] as String,
        finalContent: json['finalContent'] as String,
        scheduledDateTime: DateTime.parse(json['scheduledDateTime'] as String),
        status: PostStatus.values.firstWhere(
          (s) => s.name == json['status'],
          orElse: () => PostStatus.scheduled,
        ),
        autoPublish: json['autoPublish'] as bool? ?? true,
        errorMessage: json['errorMessage'] as String?,
        publishedAt: json['publishedAt'] != null
            ? DateTime.parse(json['publishedAt'] as String)
            : null,
        createdAt: DateTime.parse(json['createdAt'] as String),
      );
}
