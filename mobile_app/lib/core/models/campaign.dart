import 'ai_rules.dart';
import 'platform_type.dart';

/// Represents a multi-day social campaign (e.g. 30-day launch, educational blitz, or monthly content cycle).
class Campaign {
  final String id;
  final String projectId;
  final String title;
  final DateTime startDate;
  final DateTime endDate;
  final List<SocialPlatform> selectedPlatforms;
  final List<int> postingHours; // e.g. [9, 14, 18] for 9 AM, 2 PM, 6 PM
  final AiWritingRules aiRules;
  final bool autoPostingEnabled;
  final int totalPostsCount;
  final DateTime createdAt;

  Campaign({
    required this.id,
    required this.projectId,
    required this.title,
    required this.startDate,
    required this.endDate,
    required this.selectedPlatforms,
    required this.postingHours,
    required this.aiRules,
    this.autoPostingEnabled = true,
    required this.totalPostsCount,
    required this.createdAt,
  });

  int get durationInDays => endDate.difference(startDate).inDays + 1;

  Campaign copyWith({
    String? id,
    String? projectId,
    String? title,
    DateTime? startDate,
    DateTime? endDate,
    List<SocialPlatform>? selectedPlatforms,
    List<int>? postingHours,
    AiWritingRules? aiRules,
    bool? autoPostingEnabled,
    int? totalPostsCount,
    DateTime? createdAt,
  }) {
    return Campaign(
      id: id ?? this.id,
      projectId: projectId ?? this.projectId,
      title: title ?? this.title,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      selectedPlatforms: selectedPlatforms ?? this.selectedPlatforms,
      postingHours: postingHours ?? this.postingHours,
      aiRules: aiRules ?? this.aiRules,
      autoPostingEnabled: autoPostingEnabled ?? this.autoPostingEnabled,
      totalPostsCount: totalPostsCount ?? this.totalPostsCount,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'projectId': projectId,
        'title': title,
        'startDate': startDate.toIso8601String(),
        'endDate': endDate.toIso8601String(),
        'selectedPlatforms': selectedPlatforms.map((p) => p.id).toList(),
        'postingHours': postingHours,
        'aiRules': aiRules.toJson(),
        'autoPostingEnabled': autoPostingEnabled,
        'totalPostsCount': totalPostsCount,
        'createdAt': createdAt.toIso8601String(),
      };

  factory Campaign.fromJson(Map<String, dynamic> json) => Campaign(
        id: json['id'] as String,
        projectId: json['projectId'] as String,
        title: json['title'] as String,
        startDate: DateTime.parse(json['startDate'] as String),
        endDate: DateTime.parse(json['endDate'] as String),
        selectedPlatforms: (json['selectedPlatforms'] as List<dynamic>?)
                ?.map((id) => SocialPlatform.fromId(id as String))
                .toList() ??
            [SocialPlatform.linkedIn],
        postingHours: (json['postingHours'] as List<dynamic>?)
                ?.map((h) => h as int)
                .toList() ??
            [9],
        aiRules: json['aiRules'] != null
            ? AiWritingRules.fromJson(json['aiRules'] as Map<String, dynamic>)
            : const AiWritingRules(),
        autoPostingEnabled: json['autoPostingEnabled'] as bool? ?? true,
        totalPostsCount: json['totalPostsCount'] as int? ?? 30,
        createdAt: DateTime.parse(json['createdAt'] as String),
      );
}
