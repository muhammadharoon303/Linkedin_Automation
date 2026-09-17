import 'ai_rules.dart';
import 'content_document.dart';

/// A workspace project encapsulating brand identity, reference documents, and AI writing preferences.
class Project {
  final String id;
  final String name;
  final String description;
  final AiWritingRules defaultAiRules;
  final List<ContentDocument> documents;
  final DateTime createdAt;
  final DateTime updatedAt;

  Project({
    required this.id,
    required this.name,
    required this.description,
    this.defaultAiRules = const AiWritingRules(),
    this.documents = const [],
    required this.createdAt,
    required this.updatedAt,
  });

  Project copyWith({
    String? id,
    String? name,
    String? description,
    AiWritingRules? defaultAiRules,
    List<ContentDocument>? documents,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Project(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      defaultAiRules: defaultAiRules ?? this.defaultAiRules,
      documents: documents ?? this.documents,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'description': description,
        'defaultAiRules': defaultAiRules.toJson(),
        'documents': documents.map((doc) => doc.toJson()).toList(),
        'createdAt': createdAt.toIso8601String(),
        'updatedAt': updatedAt.toIso8601String(),
      };

  factory Project.fromJson(Map<String, dynamic> json) => Project(
        id: json['id'] as String,
        name: json['name'] as String,
        description: json['description'] as String? ?? '',
        defaultAiRules: json['defaultAiRules'] != null
            ? AiWritingRules.fromJson(json['defaultAiRules'] as Map<String, dynamic>)
            : const AiWritingRules(),
        documents: (json['documents'] as List<dynamic>?)
                ?.map((doc) => ContentDocument.fromJson(doc as Map<String, dynamic>))
                .toList() ??
            [],
        createdAt: DateTime.parse(json['createdAt'] as String),
        updatedAt: DateTime.parse(json['updatedAt'] as String),
      );
}
