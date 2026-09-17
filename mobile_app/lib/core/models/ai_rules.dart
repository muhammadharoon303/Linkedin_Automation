/// Configurable rules for AI content generation.
class AiWritingRules {
  final String tone; // e.g. Professional, Storytelling, Educational, Witty, Direct
  final String hookStyle; // Question, Statistic, Contrarian, Personal Story, How-To
  final String emojiDensity; // None, Minimal, Moderate, High
  final int hashtagCount; // 0 to 10
  final String callToAction; // e.g. 'Leave your thoughts below', 'Save for later'
  final String targetAudience; // e.g. 'B2B Founders', 'Software Engineers'
  final String customInstructions; // User freeform instructions

  const AiWritingRules({
    this.tone = 'Professional & Insightful',
    this.hookStyle = 'Contrarian / Thought-Provoking',
    this.emojiDensity = 'Minimal (1-3 relevant)',
    this.hashtagCount = 3,
    this.callToAction = 'What are your thoughts on this? Let me know below!',
    this.targetAudience = 'Tech professionals & founders',
    this.customInstructions = 'Use concise sentences, double line breaks between paragraphs, and avoid generic buzzwords like "delve" or "game-changer".',
  });

  AiWritingRules copyWith({
    String? tone,
    String? hookStyle,
    String? emojiDensity,
    int? hashtagCount,
    String? callToAction,
    String? targetAudience,
    String? customInstructions,
  }) {
    return AiWritingRules(
      tone: tone ?? this.tone,
      hookStyle: hookStyle ?? this.hookStyle,
      emojiDensity: emojiDensity ?? this.emojiDensity,
      hashtagCount: hashtagCount ?? this.hashtagCount,
      callToAction: callToAction ?? this.callToAction,
      targetAudience: targetAudience ?? this.targetAudience,
      customInstructions: customInstructions ?? this.customInstructions,
    );
  }

  Map<String, dynamic> toJson() => {
        'tone': tone,
        'hookStyle': hookStyle,
        'emojiDensity': emojiDensity,
        'hashtagCount': hashtagCount,
        'callToAction': callToAction,
        'targetAudience': targetAudience,
        'customInstructions': customInstructions,
      };

  factory AiWritingRules.fromJson(Map<String, dynamic> json) => AiWritingRules(
        tone: json['tone'] as String? ?? 'Professional & Insightful',
        hookStyle: json['hookStyle'] as String? ?? 'Contrarian / Thought-Provoking',
        emojiDensity: json['emojiDensity'] as String? ?? 'Minimal (1-3 relevant)',
        hashtagCount: json['hashtagCount'] as int? ?? 3,
        callToAction: json['callToAction'] as String? ?? '',
        targetAudience: json['targetAudience'] as String? ?? '',
        customInstructions: json['customInstructions'] as String? ?? '',
      );
}
