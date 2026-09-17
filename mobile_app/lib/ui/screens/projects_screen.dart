import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:provider/provider.dart';
import '../../providers/app_state.dart';
import '../../core/models/content_document.dart';
import '../../core/models/ai_rules.dart';

class ProjectsScreen extends StatefulWidget {
  const ProjectsScreen({super.key});

  @override
  State<ProjectsScreen> createState() => _ProjectsScreenState();
}

class _ProjectsScreenState extends State<ProjectsScreen> {
  void _showCreateProjectDialog() {
    final nameCtrl = TextEditingController();
    final descCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create New Project'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(
                labelText: 'Project / Brand Name',
                hintText: 'e.g. Fitness Brand, Personal Brand',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: descCtrl,
              decoration: const InputDecoration(
                labelText: 'Description',
                hintText: 'Brief goal of this project',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (nameCtrl.text.trim().isNotEmpty) {
                final appState = Provider.of<AppState>(context, listen: false);
                appState.createProject(
                  name: nameCtrl.text.trim(),
                  description: descCtrl.text.trim(),
                  rules: const AiWritingRules(),
                );
                Navigator.pop(ctx);
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }

  void _showAddDocumentModal() {
    final titleCtrl = TextEditingController();
    final contentCtrl = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 20,
          bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
        ),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Add Content Document',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Paste long-form notes, blog drafts, transcripts, or case studies for the AI to reference.',
                style: TextStyle(fontSize: 13, color: Colors.grey),
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                icon: const Icon(Icons.file_upload_outlined),
                label: const Text('Import from Text / Markdown File (.txt, .md)'),
                onPressed: () async {
                  try {
                    final files = await FilePicker.pickFiles(
                      type: FileType.custom,
                      allowedExtensions: ['txt', 'md'],
                    );
                    if (files.isNotEmpty) {
                      final file = files.first;
                      final fileName = file.name;
                      final fileContent = await file.xFile.readAsString();
                      titleCtrl.text = fileName;
                      contentCtrl.text = fileContent;
                    }
                  } catch (e) {
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('File pick error: $e')),
                      );
                    }
                  }
                },
              ),
              const SizedBox(height: 12),
              TextField(
                controller: titleCtrl,
                decoration: const InputDecoration(
                  labelText: 'Document Title',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: contentCtrl,
                maxLines: 7,
                decoration: const InputDecoration(
                  labelText: 'Content / Body Text',
                  border: OutlineInputBorder(),
                  hintText: 'Paste the source material here...',
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.save),
                  label: const Text('Save Reference Document'),
                  style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
                  onPressed: () {
                    if (titleCtrl.text.trim().isNotEmpty && contentCtrl.text.trim().isNotEmpty) {
                      final appState = Provider.of<AppState>(context, listen: false);
                      appState.addDocumentToActiveProject(
                        title: titleCtrl.text.trim(),
                        content: contentCtrl.text.trim(),
                      );
                      Navigator.pop(ctx);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Document imported successfully!')),
                      );
                    }
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showDocumentViewer(ContentDocument doc) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(doc.title),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${doc.wordCount} words • Added ${doc.addedAt.toString().substring(0, 10)}',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const Divider(height: 24),
              SelectableText(doc.content),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final appState = context.watch<AppState>();
    final activeProject = appState.activeProject;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Projects & Documents'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            tooltip: 'New Project',
            onPressed: _showCreateProjectDialog,
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Project Switcher
          Text(
            'Active Workspace / Project',
            style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14),
            decoration: BoxDecoration(
              border: Border.all(color: theme.colorScheme.outlineVariant),
              borderRadius: BorderRadius.circular(12),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: activeProject?.id,
                isExpanded: true,
                items: appState.projects.map((p) {
                  return DropdownMenuItem<String>(
                    value: p.id,
                    child: Text(
                      p.name,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  );
                }).toList(),
                onChanged: (id) {
                  if (id != null) {
                    final selected = appState.projects.firstWhere((p) => p.id == id);
                    appState.setActiveProject(selected);
                  }
                },
              ),
            ),
          ),
          const SizedBox(height: 8),
          if (activeProject != null)
            Text(
              activeProject.description,
              style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.outline),
            ),
          const Divider(height: 36),

          // Documents Library Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Content Document Library',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '${activeProject?.documents.length ?? 0} reference docs',
                    style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.outline),
                  ),
                ],
              ),
              ElevatedButton.icon(
                icon: const Icon(Icons.add, size: 18),
                label: const Text('Add Document'),
                onPressed: _showAddDocumentModal,
              ),
            ],
          ),
          const SizedBox(height: 12),

          if (activeProject == null || activeProject.documents.isEmpty)
            Container(
              padding: const EdgeInsets.all(28),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest.withAlpha(30),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: theme.colorScheme.outlineVariant.withAlpha(50)),
              ),
              child: Column(
                children: [
                  const Icon(Icons.note_add_outlined, size: 40, color: Colors.grey),
                  const SizedBox(height: 10),
                  const Text(
                    'No documents added yet',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Import files or paste your blog posts so Ollama can ground post generation in your real expertise.',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            )
          else
            ...activeProject.documents.map((doc) {
              return Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: BorderSide(color: theme.colorScheme.outlineVariant.withAlpha(60)),
                ),
                margin: const EdgeInsets.only(bottom: 10),
                child: ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: Colors.teal,
                    child: Icon(Icons.description, color: Colors.white, size: 20),
                  ),
                  title: Text(doc.title, style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(
                    '${doc.wordCount} words • Added ${doc.addedAt.toString().substring(0, 10)}',
                  ),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
                    onPressed: () => appState.removeDocument(doc.id),
                  ),
                  onTap: () => _showDocumentViewer(doc),
                ),
              );
            }),
        ],
      ),
    );
  }
}
