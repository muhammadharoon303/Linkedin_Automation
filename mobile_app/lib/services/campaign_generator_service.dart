import 'package:uuid/uuid.dart';
import '../core/models/project.dart';
import '../core/models/campaign.dart';
import '../core/models/scheduled_post.dart';
import '../core/models/platform_type.dart';
import '../core/models/ai_rules.dart';
import 'api_service.dart';

class CampaignGeneratorService {
  final ApiService _apiService;
  final Uuid _uuid = const Uuid();

  CampaignGeneratorService(this._apiService);

  // A 30-day topical content pillar rotation framework
  static const List<String> _topicArchetypes = [
    'The #1 myth in {topic} and why it holds you back',
    '3 unexpected lessons learned after 100 days of {topic}',
    'How to achieve 10x results in {topic} without burning out',
    'The exact tech stack and tools we use for {topic}',
    'A painful mistake we made in {topic} and how to avoid it',
    'Why traditional methods in {topic} are failing in 2026',
    'A 5-minute step-by-step framework for mastering {topic}',
    'Contrarian opinion: Why most advice about {topic} is wrong',
    'The single metric that actually matters when evaluating {topic}',
    'How to transition from beginner to advanced in {topic}',
  ];

  /// Generates a complete 30-day campaign along with scheduled post drafts across all chosen platforms.
  Future<({Campaign campaign, List<ScheduledPost> posts})> generate30DayCampaign({
    required Project project,
    required String campaignTitle,
    required DateTime startDate,
    required DateTime endDate,
    required List<SocialPlatform> platforms,
    required List<int> postingHours,
    required AiWritingRules rules,
    required bool autoPostingEnabled,
    String? baseTopic,
    String? model,
  }) async {
    final campaignId = _uuid.v4();
    final effectiveTopic = baseTopic?.isNotEmpty == true
        ? baseTopic!
        : (project.documents.isNotEmpty
            ? project.documents.first.title
            : project.name);

    final referenceContext = project.documents.isNotEmpty
        ? project.documents.map((d) => d.content).join('\n---\n')
        : null;

    final days = endDate.difference(startDate).inDays + 1;
    final List<ScheduledPost> generatedPosts = [];

    // Extract day-by-day topics directly from documents if formatted as Day 1, Day 2, or numbered list
    final List<String> extractedDayTopics = [];
    if (project.documents.isNotEmpty) {
      for (final doc in project.documents) {
        final lines = doc.content.split('\n').map((l) => l.trim()).toList();
        for (final line in lines) {
          final match = RegExp(r'^(?:Day\s*\d+[:.-]?|\d+[.)])\s*(.*)$', caseSensitive: false).firstMatch(line);
          if (match != null && match.group(1)?.trim().isNotEmpty == true) {
            extractedDayTopics.add(match.group(1)!.trim());
          }
        }
      }
    }

    // Distribute posts across each day
    for (int dayIndex = 0; dayIndex < days; dayIndex++) {
      final postDate = startDate.add(Duration(days: dayIndex));
      String currentTopic;
      if (dayIndex < extractedDayTopics.length) {
        currentTopic = extractedDayTopics[dayIndex];
      } else {
        final topicTemplate = _topicArchetypes[dayIndex % _topicArchetypes.length];
        currentTopic = topicTemplate.replaceAll('{topic}', effectiveTopic);
      }

      for (final platform in platforms) {
        for (final hour in postingHours) {
          final postDateTime = DateTime(
            postDate.year,
            postDate.month,
            postDate.day,
            hour,
            0,
          );

          // Generate initial content via API service
          final content = await _apiService.generateContent(
            platform: platform,
            topic: currentTopic,
            rules: rules,
            referenceContext: referenceContext,
            model: model ?? 'llama3',
          );

          final post = ScheduledPost(
            id: _uuid.v4(),
            projectId: project.id,
            campaignId: campaignId,
            platform: platform,
            topic: currentTopic,
            hook: 'Day ${dayIndex + 1}: $currentTopic',
            generatedContent: content,
            finalContent: content,
            scheduledDateTime: postDateTime,
            status: PostStatus.scheduled,
            autoPublish: autoPostingEnabled,
            createdAt: DateTime.now(),
          );

          generatedPosts.add(post);
        }
      }
    }

    final campaign = Campaign(
      id: campaignId,
      projectId: project.id,
      title: campaignTitle,
      startDate: startDate,
      endDate: endDate,
      selectedPlatforms: platforms,
      postingHours: postingHours,
      aiRules: rules,
      autoPostingEnabled: autoPostingEnabled,
      totalPostsCount: generatedPosts.length,
      createdAt: DateTime.now(),
    );

    return (campaign: campaign, posts: generatedPosts);
  }
}
