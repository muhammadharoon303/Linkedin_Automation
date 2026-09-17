import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/models/project.dart';
import '../core/models/campaign.dart';
import '../core/models/scheduled_post.dart';
import '../core/models/content_document.dart';
import '../core/models/ai_rules.dart';
import '../core/models/platform_type.dart';

/// Local JSON-based storage using SharedPreferences for offline-first persistence.
class StorageService {
  static const String _keyProjects = 'sa_projects';
  static const String _keyCampaigns = 'sa_campaigns';
  static const String _keyPosts = 'sa_posts';
  static const String _keyActiveProjectId = 'sa_active_project_id';
  static const String _keyBackendUrl = 'sa_backend_url';
  static const String _keyOllamaModel = 'sa_ollama_model';

  final SharedPreferences _prefs;

  StorageService(this._prefs);

  static Future<StorageService> init() async {
    final prefs = await SharedPreferences.getInstance();
    final service = StorageService(prefs);
    await service._seedInitialDataIfEmpty();
    return service;
  }

  // Backend settings
  String getBackendUrl() {
    // 10.0.2.2 is Android Emulator's alias to host 127.0.0.1.
    // For physical device, user can enter their PC LAN IP in Settings.
    return _prefs.getString(_keyBackendUrl) ?? 'http://10.0.2.2:8000';
  }

  Future<void> saveBackendUrl(String url) async {
    await _prefs.setString(_keyBackendUrl, url);
  }

  String getOllamaModel() {
    return _prefs.getString(_keyOllamaModel) ?? 'llama3';
  }

  Future<void> saveOllamaModel(String model) async {
    await _prefs.setString(_keyOllamaModel, model);
  }

  // Active project ID
  String? getActiveProjectId() {
    return _prefs.getString(_keyActiveProjectId);
  }

  Future<void> saveActiveProjectId(String id) async {
    await _prefs.setString(_keyActiveProjectId, id);
  }

  // Projects
  List<Project> loadProjects() {
    final raw = _prefs.getString(_keyProjects);
    if (raw == null || raw.isEmpty) return [];
    try {
      final List<dynamic> list = jsonDecode(raw);
      return list.map((item) => Project.fromJson(item as Map<String, dynamic>)).toList();
    } catch (_) {
      return [];
    }
  }

  Future<void> saveProjects(List<Project> projects) async {
    final raw = jsonEncode(projects.map((p) => p.toJson()).toList());
    await _prefs.setString(_keyProjects, raw);
  }

  // Campaigns
  List<Campaign> loadCampaigns() {
    final raw = _prefs.getString(_keyCampaigns);
    if (raw == null || raw.isEmpty) return [];
    try {
      final List<dynamic> list = jsonDecode(raw);
      return list.map((item) => Campaign.fromJson(item as Map<String, dynamic>)).toList();
    } catch (_) {
      return [];
    }
  }

  Future<void> saveCampaigns(List<Campaign> campaigns) async {
    final raw = jsonEncode(campaigns.map((c) => c.toJson()).toList());
    await _prefs.setString(_keyCampaigns, raw);
  }

  // Scheduled Posts
  List<ScheduledPost> loadPosts() {
    final raw = _prefs.getString(_keyPosts);
    if (raw == null || raw.isEmpty) return [];
    try {
      final List<dynamic> list = jsonDecode(raw);
      return list.map((item) => ScheduledPost.fromJson(item as Map<String, dynamic>)).toList();
    } catch (_) {
      return [];
    }
  }

  Future<void> savePosts(List<ScheduledPost> posts) async {
    final raw = jsonEncode(posts.map((p) => p.toJson()).toList());
    await _prefs.setString(_keyPosts, raw);
  }

  /// Seeds default projects and sample campaign so first-time users can immediately test the UI.
  Future<void> _seedInitialDataIfEmpty() async {
    if (_prefs.getString(_keyProjects) == null) {
      final now = DateTime.now();

      final defaultDoc = ContentDocument(
        id: 'doc-welcome-01',
        projectId: 'proj-default-01',
        title: 'B2B SaaS Growth & AI Automation Playbook',
        content: '''
Title: Why AI Automation is Revolutionizing Organic Social Growth
Key Insights:
1. Consistency beats perfection: Publishing daily compound returns over 6-12 months.
2. Repurposing 1 long-form asset into 5 modular hooks produces 10x output with zero extra research.
3. Engaging hooks that challenge popular misconceptions get 300% more comments.
4. Always end with an open question to trigger algorithm distribution.
        ''',
        wordCount: 65,
        addedAt: now.subtract(const Duration(days: 2)),
      );

      final defaultProject = Project(
        id: 'proj-default-01',
        name: 'Muhammad Haroon - Tech Brand',
        description: 'Personal thought leadership and content automation for Muhammad Haroon across LinkedIn and TikTok.',
        defaultAiRules: const AiWritingRules(
          tone: 'Thought-Provoking & Actionable',
          hookStyle: 'Contrarian / Misconception',
          emojiDensity: 'Minimal (1-2 relevant)',
          hashtagCount: 3,
          callToAction: 'What is your biggest bottleneck with organic content? Comment below!',
          targetAudience: 'Software engineers, founders, and content creators',
        ),
        documents: [defaultDoc],
        createdAt: now.subtract(const Duration(days: 2)),
        updatedAt: now,
      );

      final defaultCampaign = Campaign(
        id: 'camp-30day-01',
        projectId: 'proj-default-01',
        title: '30-Day LinkedIn & TikTok Authority Campaign',
        startDate: now,
        endDate: now.add(const Duration(days: 30)),
        selectedPlatforms: [SocialPlatform.linkedIn, SocialPlatform.tikTok, SocialPlatform.twitter],
        postingHours: [9, 17],
        aiRules: defaultProject.defaultAiRules,
        autoPostingEnabled: true,
        totalPostsCount: 6,
        createdAt: now,
      );

      final samplePosts = [
        ScheduledPost(
          id: 'post-seed-01',
          projectId: 'proj-default-01',
          campaignId: 'camp-30day-01',
          platform: SocialPlatform.linkedIn,
          topic: 'The #1 mistake founders make when posting on LinkedIn',
          hook: 'Most founders treat LinkedIn like a resume. That is why nobody reads their posts.',
          generatedContent: '''Most founders treat LinkedIn like a resume. That is why nobody reads their posts.

Here is what actually works in 2026:
• Share the painful lessons from your failed launches
• Breakdown your daily architecture decisions
• Disagree with conventional industry "best practices"

Consistency beats production value every single time.

What is your biggest bottleneck with organic content? Comment below!

#LinkedInTips #FounderJourney #BuildingInPublic''',
          finalContent: '''Most founders treat LinkedIn like a resume. That is why nobody reads their posts.

Here is what actually works in 2026:
• Share the painful lessons from your failed launches
• Breakdown your daily architecture decisions
• Disagree with conventional industry "best practices"

Consistency beats production value every single time.

What is your biggest bottleneck with organic content? Comment below!

#LinkedInTips #FounderJourney #BuildingInPublic''',
          scheduledDateTime: now.add(const Duration(hours: 3)),
          status: PostStatus.scheduled,
          autoPublish: true,
          createdAt: now,
        ),
        ScheduledPost(
          id: 'post-seed-02',
          projectId: 'proj-default-01',
          campaignId: 'camp-30day-01',
          platform: SocialPlatform.tikTok,
          topic: 'Stop building in secret: 3-step blueprint',
          hook: 'If nobody knows your app exists, your code quality does not matter.',
          generatedContent: '''[HOOK - 0:00-0:03]: If nobody knows your app exists, your code quality doesn't matter.
[SCENE 1 - 0:03-0:15]: Most devs spend 6 months perfecting an auth flow nobody will ever log into.
[SCENE 2 - 0:15-0:30]: Instead, document your build from day 1 on TikTok and X.
[SCENE 3 - 0:30-0:45]: Use local AI to turn your commit messages into daily bite-sized lessons.
[CTA - 0:45-0:60]: Follow for real dev stories without the hype.

#BuildInPublic #DevTok #CodingLife #SoftwareEngineer''',
          finalContent: '''[HOOK - 0:00-0:03]: If nobody knows your app exists, your code quality doesn't matter.
[SCENE 1 - 0:03-0:15]: Most devs spend 6 months perfecting an auth flow nobody will ever log into.
[SCENE 2 - 0:15-0:30]: Instead, document your build from day 1 on TikTok and X.
[SCENE 3 - 0:30-0:45]: Use local AI to turn your commit messages into daily bite-sized lessons.
[CTA - 0:45-0:60]: Follow for real dev stories without the hype.

#BuildInPublic #DevTok #CodingLife #SoftwareEngineer''',
          scheduledDateTime: now.add(const Duration(hours: 8)),
          status: PostStatus.scheduled,
          autoPublish: true,
          createdAt: now,
        ),
        ScheduledPost(
          id: 'post-seed-03',
          projectId: 'proj-default-01',
          campaignId: 'camp-30day-01',
          platform: SocialPlatform.linkedIn,
          topic: 'Why we switched from Cloud APIs to Local Ollama',
          hook: 'We cut our monthly AI API bill to \$0 by running Ollama locally.',
          generatedContent: '''We cut our monthly AI API bill to \$0 by running Ollama locally.

When you are generating 100+ social posts across a 30-day campaign, token fees add up fast.

By pairing FastAPI with a local quantized model:
1. 100% privacy for unpublished strategy docs
2. Zero per-request charges
3. Works completely offline

Privacy and cost efficiency can coexist.

Have you tried running local LLMs in production yet?

#OpenSource #AI #Ollama #SelfHosting''',
          finalContent: '''We cut our monthly AI API bill to \$0 by running Ollama locally.

When you are generating 100+ social posts across a 30-day campaign, token fees add up fast.

By pairing FastAPI with a local quantized model:
1. 100% privacy for unpublished strategy docs
2. Zero per-request charges
3. Works completely offline

Privacy and cost efficiency can coexist.

Have you tried running local LLMs in production yet?

#OpenSource #AI #Ollama #SelfHosting''',
          scheduledDateTime: now.subtract(const Duration(days: 1)),
          status: PostStatus.published,
          autoPublish: true,
          publishedAt: now.subtract(const Duration(days: 1)),
          createdAt: now.subtract(const Duration(days: 2)),
        ),
      ];

      await saveProjects([defaultProject]);
      await saveCampaigns([defaultCampaign]);
      await savePosts(samplePosts);
      await saveActiveProjectId(defaultProject.id);
    }
  }
}
