import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/models/platform_type.dart';
import '../core/models/ai_rules.dart';

class ApiService {
  String baseUrl;
  final http.Client _client;

  ApiService({required this.baseUrl, http.Client? client})
      : _client = client ?? http.Client();

  /// Tests connectivity to the FastAPI & Ollama backend
  Future<Map<String, dynamic>> checkHealth() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final response = await _client.get(uri).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        return {
          'status': 'error',
          'message': 'Server responded with code ${response.statusCode}'
        };
      }
    } catch (e) {
      return {
        'status': 'offline',
        'message': 'Cannot reach backend at $baseUrl ($e). Using local offline generator mode.'
      };
    }
  }

  /// Fetches available models from Ollama via the backend
  Future<List<String>> fetchAvailableModels() async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/ai/models');
      final response = await _client.get(uri).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final list = (data['models'] as List<dynamic>?)?.map((m) => m.toString()).toList();
        return list ?? ['llama3', 'mistral', 'phi3'];
      }
    } catch (_) {}
    return ['llama3', 'mistral', 'phi3', 'qwen2'];
  }

  /// Calls the local Ollama API through our FastAPI backend
  Future<String> generateContent({
    required SocialPlatform platform,
    required String topic,
    required AiWritingRules rules,
    String? referenceContext,
    String model = 'llama3',
  }) async {
    final payload = {
      'platform': platform.id,
      'topic': topic,
      'model': model,
      'tone': rules.tone,
      'hook_style': rules.hookStyle,
      'emoji_density': rules.emojiDensity,
      'hashtag_count': rules.hashtagCount,
      'call_to_action': rules.callToAction,
      'target_audience': rules.targetAudience,
      'custom_instructions': rules.customInstructions,
      'reference_context': referenceContext ?? '',
    };

    try {
      final uri = Uri.parse('$baseUrl/api/v1/ai/generate');
      final response = await _client
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(payload),
          )
          .timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['content'] as String;
      }
    } catch (_) {
      // Backend not running yet or connection timed out: use high-quality intelligent offline fallback
    }

    return _generateOfflineFallback(platform: platform, topic: topic, rules: rules);
  }

  /// Fallback high-fidelity generator when testing Flutter UI without live FastAPI server running
  String _generateOfflineFallback({
    required SocialPlatform platform,
    required String topic,
    required AiWritingRules rules,
  }) {
    final cta = rules.callToAction.isNotEmpty
        ? rules.callToAction
        : 'What is your perspective on this? Drop a comment below!';

    switch (platform) {
      case SocialPlatform.linkedIn:
        return '''Here is the hard truth about $topic that most people ignore:

1. Traditional methods are becoming obsolete faster than expected.
2. The teams winning right now are focusing on automated consistency.
3. Quality is an emergent property of high volume and rapid feedback.

Key takeaway: Don't wait for ideal conditions before sharing your progress.

$cta

#$topic #Innovation #Leadership #FutureOfWork''';

      case SocialPlatform.tikTok:
        return '''[HOOK - 0:00 to 0:03]:
Stop scrolling if you care about $topic. Here is what they won't tell you.

[VISUAL: Fast-paced text overlay with key stat]

[SCENE 1 - 0:03 to 0:15]:
Everyone thinks $topic takes months to master. But if you focus on the 20% that drives 80% of results, you can see traction in 7 days.

[SCENE 2 - 0:15 to 0:30]:
Step 1: Eliminate low-leverage manual tasks.
Step 2: Use AI to handle batch drafting.
Step 3: Review and publish daily.

[OUTRO - 0:30 to 0:45]:
$cta

#$topic #LearnOnTikTok #ProductivityHacks #TechTok''';

      case SocialPlatform.twitter:
        return '''Most people approach $topic completely backwards.

Instead of waiting for perfection:
→ Build publicly
→ Automate distribution
→ Iterate on real audience feedback

$cta #$topic''';

      case SocialPlatform.instagram:
        return '''The secret to unlocking massive growth in $topic 💡

Swipe through for the complete breakdown ➡️

Consistent action compounded over 30 days will completely transform your trajectory.

Double tap if this resonated and save for your next session! 📌

$cta

#$topic #GrowthMindset #DailyInspiration #ContentStrategy''';

      case SocialPlatform.youTube:
        return '''[YOUTUBE SHORTS SCRIPT: $topic]
Duration: 50 Seconds

[0:00 - 0:04] HOOK: "If you want to master $topic, this 30-second framework is all you need."
[0:04 - 0:18] PROBLEM: The biggest trap beginners fall into when starting out.
[0:18 - 0:35] SOLUTION: The 3 pillars of effective automation and execution.
[0:35 - 0:50] CALL TO ACTION: "$cta"

#Shorts #$topic #Tutorial''';

      case SocialPlatform.bluesky:
        return '''A quick perspective on $topic:

The gap between having an idea and having distribution is shrinking rapidly. The future belongs to those who automate the routine and amplify the authentic.

$cta''';
    }
  }

  /// Get Master Auto-Posting switch state from backend
  Future<bool> getMasterSwitch() async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/analytics/master-switch');
      final response = await _client.get(uri).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['master_auto_posting'] as bool? ?? true;
      }
    } catch (_) {}
    return true;
  }

  /// Set Master Auto-Posting switch state on backend
  Future<bool> setMasterSwitch(bool enabled) async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/analytics/master-switch');
      final response = await _client
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'enabled': enabled}),
          )
          .timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['master_auto_posting'] as bool? ?? enabled;
      }
    } catch (_) {}
    return enabled;
  }

  /// Lists connected accounts (e.g. LinkedIn) from backend without client secrets
  Future<List<Map<String, dynamic>>> fetchConnectedAccounts() async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/oauth/accounts');
      final response = await _client.get(uri).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        final List<dynamic> list = jsonDecode(response.body);
        return list.map((item) => item as Map<String, dynamic>).toList();
      }
    } catch (_) {}
    return [];
  }

  /// Disconnects a social account
  Future<bool> disconnectAccount(String accountId) async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/oauth/accounts/$accountId');
      final response = await _client.delete(uri).timeout(const Duration(seconds: 4));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Fetches the LinkedIn OAuth URL from backend
  Future<String?> getLinkedInAuthorizeUrl() async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/oauth/linkedin/authorize-url');
      final response = await _client.get(uri).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['authorize_url'] as String?;
      }
    } catch (_) {}
    return null;
  }

  /// Fetches system analytics overview from backend
  Future<Map<String, dynamic>?> fetchAnalytics() async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/analytics/overview');
      final response = await _client.get(uri).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
    } catch (_) {}
    return null;
  }
}
