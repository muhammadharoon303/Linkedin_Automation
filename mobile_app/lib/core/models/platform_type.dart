import 'package:flutter/material.dart';

/// Supported social media platforms.
/// Designed modularly so new platforms (e.g. Threads, Reddit, Pinterest) can be added seamlessly.
enum SocialPlatform {
  linkedIn,
  tikTok,
  twitter,
  instagram,
  youTube,
  bluesky;

  String get id {
    switch (this) {
      case SocialPlatform.linkedIn:
        return 'linkedin';
      case SocialPlatform.tikTok:
        return 'tiktok';
      case SocialPlatform.twitter:
        return 'twitter';
      case SocialPlatform.instagram:
        return 'instagram';
      case SocialPlatform.youTube:
        return 'youtube';
      case SocialPlatform.bluesky:
        return 'bluesky';
    }
  }

  String get displayName {
    switch (this) {
      case SocialPlatform.linkedIn:
        return 'LinkedIn';
      case SocialPlatform.tikTok:
        return 'TikTok';
      case SocialPlatform.twitter:
        return 'X (Twitter)';
      case SocialPlatform.instagram:
        return 'Instagram';
      case SocialPlatform.youTube:
        return 'YouTube Shorts';
      case SocialPlatform.bluesky:
        return 'Bluesky';
    }
  }

  Color get brandColor {
    switch (this) {
      case SocialPlatform.linkedIn:
        return const Color(0xFF0A66C2);
      case SocialPlatform.tikTok:
        return const Color(0xFFFE2C55);
      case SocialPlatform.twitter:
        return const Color(0xFF1D9BF0);
      case SocialPlatform.instagram:
        return const Color(0xFFE4405F);
      case SocialPlatform.youTube:
        return const Color(0xFFFF0000);
      case SocialPlatform.bluesky:
        return const Color(0xFF0560FF);
    }
  }

  IconData get icon {
    switch (this) {
      case SocialPlatform.linkedIn:
        return Icons.business_center;
      case SocialPlatform.tikTok:
        return Icons.music_video;
      case SocialPlatform.twitter:
        return Icons.tag;
      case SocialPlatform.instagram:
        return Icons.camera_alt;
      case SocialPlatform.youTube:
        return Icons.play_circle_fill;
      case SocialPlatform.bluesky:
        return Icons.cloud_queue;
    }
  }

  int get maxCharacterCount {
    switch (this) {
      case SocialPlatform.linkedIn:
        return 3000;
      case SocialPlatform.tikTok:
        return 2200; // Caption limit
      case SocialPlatform.twitter:
        return 280;
      case SocialPlatform.instagram:
        return 2200;
      case SocialPlatform.youTube:
        return 5000;
      case SocialPlatform.bluesky:
        return 300;
    }
  }

  String get defaultHookPrompt {
    switch (this) {
      case SocialPlatform.linkedIn:
        return 'Write a compelling professional hook, followed by actionable lessons or insights, structured with bullet points, and ending with a discussion question.';
      case SocialPlatform.tikTok:
        return 'Write an attention-grabbing 3-second spoken video script hook and a high-converting caption with 3-5 trending hashtags.';
      case SocialPlatform.twitter:
        return 'Write a punchy, concise tweet under 280 characters that sparks curiosity or debate with 1-2 relevant hashtags.';
      case SocialPlatform.instagram:
        return 'Write an engaging caption with a strong first-line headline, clean spacing, valuable takeaways, and a call to save/share.';
      case SocialPlatform.youTube:
        return 'Write a 60-second YouTube Shorts video script with timing cues, visual cues [B-roll], and spoken voiceover.';
      case SocialPlatform.bluesky:
        return 'Write a clear, thoughtful micro-post under 300 characters.';
    }
  }

  static SocialPlatform fromId(String id) {
    return SocialPlatform.values.firstWhere(
      (p) => p.id == id.toLowerCase(),
      orElse: () => SocialPlatform.linkedIn,
    );
  }
}
