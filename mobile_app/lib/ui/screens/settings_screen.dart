import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/app_state.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _urlController;
  String? _selectedModel;

  @override
  void initState() {
    super.initState();
    final appState = Provider.of<AppState>(context, listen: false);
    _urlController = TextEditingController(text: appState.backendUrl);
    _selectedModel = appState.ollamaModel;
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  void _saveSettings() async {
    final appState = Provider.of<AppState>(context, listen: false);
    await appState.setBackendUrl(_urlController.text.trim());
    if (_selectedModel != null) {
      await appState.setOllamaModel(_selectedModel!);
    }
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Settings saved & backend re-checked!')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final appState = context.watch<AppState>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Backend & AI Engine Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Backend Connection Card
          Card(
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: BorderSide(color: theme.colorScheme.outlineVariant.withAlpha(80)),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.dns, color: Colors.blue),
                      const SizedBox(width: 8),
                      Text(
                        'FastAPI Local Server',
                        style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      const Spacer(),
                      Chip(
                        label: Text(appState.backendStatus.toUpperCase()),
                        backgroundColor: appState.backendStatus == 'online'
                            ? Colors.green.withAlpha(30)
                            : Colors.amber.withAlpha(30),
                        labelStyle: TextStyle(
                          color: appState.backendStatus == 'online'
                              ? Colors.green[800]
                              : Colors.amber[900],
                          fontWeight: FontWeight.bold,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _urlController,
                    decoration: InputDecoration(
                      labelText: 'Backend URL',
                      helperText:
                          'Use "http://10.0.2.2:8000" for Android Emulator, or "http://<PC_IP>:8000" for physical Android phone over Wi-Fi.',
                      helperMaxLines: 3,
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    icon: const Icon(Icons.refresh),
                    label: const Text('Test Connection & Refresh Models'),
                    onPressed: () => appState.checkBackendHealth(),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Ollama Model Configuration
          Card(
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: BorderSide(color: theme.colorScheme.outlineVariant.withAlpha(80)),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.memory, color: Colors.purple),
                      const SizedBox(width: 8),
                      Text(
                        'Ollama Local Model',
                        style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    initialValue: appState.availableModels.contains(_selectedModel)
                        ? _selectedModel
                        : appState.availableModels.first,
                    decoration: InputDecoration(
                      labelText: 'Selected Model',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    items: appState.availableModels
                        .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                        .toList(),
                    onChanged: (val) {
                      setState(() => _selectedModel = val);
                    },
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '100% Free & offline execution via Ollama (no OpenAI or third-party token costs).',
                    style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.outline),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Connected Social Accounts Card
          Card(
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: BorderSide(color: theme.colorScheme.outlineVariant.withAlpha(80)),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.link, color: Color(0xFF0A66C2)),
                      const SizedBox(width: 8),
                      Text(
                        'Connected Accounts & Official APIs',
                        style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Tokens are stored securely on your local FastAPI backend and never exposed inside Flutter.',
                    style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.outline),
                  ),
                  const SizedBox(height: 16),
                  if (appState.connectedAccounts.isEmpty)
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest.withAlpha(50),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.info_outline, size: 18, color: Colors.grey),
                          SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'No accounts connected yet. Connect LinkedIn using official OAuth below.',
                              style: TextStyle(fontSize: 12),
                            ),
                          ),
                        ],
                      ),
                    )
                  else
                    ...appState.connectedAccounts.map((acc) {
                      return ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: const CircleAvatar(
                          backgroundColor: Color(0xFF0A66C2),
                          child: Icon(Icons.business_center, color: Colors.white, size: 18),
                        ),
                        title: Text(
                          acc['account_name'] ?? 'Social Account',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                        subtitle: Text(
                          '${acc['platform'].toString().toUpperCase()} • Active',
                          style: const TextStyle(fontSize: 11, color: Colors.green),
                        ),
                        trailing: IconButton(
                          icon: const Icon(Icons.link_off, color: Colors.redAccent, size: 20),
                          tooltip: 'Disconnect',
                          onPressed: () => appState.disconnectSocialAccount(acc['id']),
                        ),
                      );
                    }),
                  const SizedBox(height: 14),
                  OutlinedButton.icon(
                    icon: const Icon(Icons.add_link, color: Color(0xFF0A66C2)),
                    label: const Text(
                      'Connect LinkedIn (Official OAuth 2.0)',
                      style: TextStyle(color: Color(0xFF0A66C2)),
                    ),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Color(0xFF0A66C2)),
                    ),
                    onPressed: () async {
                      final url = await appState.apiService.getLinkedInAuthorizeUrl();
                      if (context.mounted) {
                        showDialog(
                          context: context,
                          builder: (ctx) => AlertDialog(
                            title: const Text('Connect LinkedIn via OAuth 2.0'),
                            content: Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  '1. Official Scope: w_member_social (100% Free, personal profile posting).\n'
                                  '2. Tokens are handled exclusively by your local FastAPI backend.\n\n'
                                  'To authenticate, open this official LinkedIn OAuth URL in your browser:',
                                  style: TextStyle(fontSize: 13),
                                ),
                                const SizedBox(height: 12),
                                SelectableText(
                                  url ?? '${appState.backendUrl}/api/v1/oauth/linkedin/authorize-url',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: Colors.blue,
                                    fontFamily: 'monospace',
                                  ),
                                ),
                              ],
                            ),
                            actions: [
                              TextButton(
                                onPressed: () {
                                  Navigator.pop(ctx);
                                  appState.refreshConnectedAccounts();
                                },
                                child: const Text('Done / Refresh'),
                              ),
                            ],
                          ),
                        );
                      }
                    },
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: theme.colorScheme.primary,
              foregroundColor: theme.colorScheme.onPrimary,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            onPressed: _saveSettings,
            child: const Text('Save Settings', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}
