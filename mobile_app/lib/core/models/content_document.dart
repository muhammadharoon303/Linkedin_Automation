/// Represents a source document (e.g. blog post, product note, transcript, case study)
/// imported into a project for the AI to extract topics and insights from.
class ContentDocument {
  final String id;
  final String projectId;
  final String title;
  final String content;
  final String? sourcePath;
  final int wordCount;
  final DateTime addedAt;

  ContentDocument({
    required this.id,
    required this.projectId,
    required this.title,
    required this.content,
    this.sourcePath,
    required this.wordCount,
    required this.addedAt,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'projectId': projectId,
        'title': title,
        'content': content,
        'sourcePath': sourcePath,
        'wordCount': wordCount,
        'addedAt': addedAt.toIso8601String(),
      };

  factory ContentDocument.fromJson(Map<String, dynamic> json) =>
      ContentDocument(
        id: json['id'] as String,
        projectId: json['projectId'] as String,
        title: json['title'] as String,
        content: json['content'] as String,
        sourcePath: json['sourcePath'] as String?,
        wordCount: json['wordCount'] as int? ?? 0,
        addedAt: DateTime.parse(json['addedAt'] as String),
      );
}
