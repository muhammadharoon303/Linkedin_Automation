import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../../providers/app_state.dart';
import '../../core/models/platform_type.dart';
import '../../core/models/ai_rules.dart';
import '../widgets/platform_badge.dart';

class CampaignBuilderScreen extends StatefulWidget {
  const CampaignBuilderScreen({super.key});

  @override
  State<CampaignBuilderScreen> createState() => _CampaignBuilderScreenState();
}

class _CampaignBuilderScreenState extends State<CampaignBuilderScreen> {
  final _formKey = GlobalKey<FormState>();

  late TextEditingController _titleController;
  late TextEditingController _topicController;
  late TextEditingController _documentController;
  late TextEditingController _ctaController;
  late TextEditingController _targetAudienceController;
  late TextEditingController _customInstructionsController;

  late DateTime _startDate;
  late DateTime _endDate;
  final Set<SocialPlatform> _selectedPlatforms = {
    SocialPlatform.linkedIn,
    SocialPlatform.tikTok,
  };
  final List<int> _postingHours = [9]; // Default 9 AM daily (1 post per day)
  bool _autoPostingEnabled = true;

  String _tone = 'Professional & Insightful';
  String _hookStyle = 'Contrarian / Thought-Provoking';
  String _emojiDensity = 'Minimal (1-3 relevant)';
  double _hashtagCount = 3;

  final List<String> _tones = [
    'Professional & Insightful',
    'Casual & Conversational',
    'Storytelling & Vulnerable',
    'Educational & Step-by-Step',
    'Witty & Bold',
    'Authoritative Thought Leader',
  ];

  final List<String> _hookStyles = [
    'Contrarian / Thought-Provoking',
    'Shocking Statistic / Fact',
    'Personal Failure to Breakthrough',
    'Direct How-To / Cheat Sheet',
    'Engaging Question / Debate',
  ];

  final List<String> _emojiDensities = [
    'None (Text only)',
    'Minimal (1-3 relevant)',
    'Moderate (Bullets & hooks)',
    'High (Dynamic & expressive)',
  ];

  @override
  void initState() {
    super.initState();
    final appState = Provider.of<AppState>(context, listen: false);
    final activeRules = appState.activeProject?.defaultAiRules ?? const AiWritingRules();

    _titleController = TextEditingController(text: '30-Day Omnichannel Authority Campaign');
    _topicController = TextEditingController(
      text: appState.activeProject?.documents.isNotEmpty == true
          ? appState.activeProject!.documents.first.title
          : 'AI Automation & SaaS Growth',
    );
    _ctaController = TextEditingController(text: activeRules.callToAction);
    _targetAudienceController = TextEditingController(text: activeRules.targetAudience);
    _customInstructionsController =
        TextEditingController(text: activeRules.customInstructions);
    _documentController = TextEditingController();

    _startDate = DateTime.now();
    _endDate = _startDate.add(const Duration(days: 30));
  }

  @override
  void dispose() {
    _titleController.dispose();
    _topicController.dispose();
    _documentController.dispose();
    _ctaController.dispose();
    _targetAudienceController.dispose();
    _customInstructionsController.dispose();
    super.dispose();
  }

  Future<void> _pickStartDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _startDate,
      firstDate: DateTime.now().subtract(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null) {
      setState(() {
        _startDate = picked;
        if (_endDate.isBefore(_startDate)) {
          _endDate = _startDate.add(const Duration(days: 30));
        }
      });
    }
  }

  Future<void> _pickEndDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _endDate,
      firstDate: _startDate,
      lastDate: _startDate.add(const Duration(days: 365)),
    );
    if (picked != null) {
      setState(() {
        _endDate = picked;
      });
    }
  }

  void _addPostingHour() async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: const TimeOfDay(hour: 12, minute: 0),
    );
    if (picked != null && !_postingHours.contains(picked.hour)) {
      setState(() {
        _postingHours.add(picked.hour);
        _postingHours.sort();
      });
    }
  }

  int get _calculatedPostTotal {
    final days = _endDate.difference(_startDate).inDays + 1;
    return days * _selectedPlatforms.length * _postingHours.length;
  }

  Future<void> _generateCampaign() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedPlatforms.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one social media platform.')),
      );
      return;
    }
    if (_postingHours.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one posting time slot.')),
      );
      return;
    }

    final appState = Provider.of<AppState>(context, listen: false);

    final configuredRules = AiWritingRules(
      tone: _tone,
      hookStyle: _hookStyle,
      emojiDensity: _emojiDensity,
      hashtagCount: _hashtagCount.round(),
      callToAction: _ctaController.text.trim(),
      targetAudience: _targetAudienceController.text.trim(),
      customInstructions: _customInstructionsController.text.trim(),
    );

    // Ingest master document if user pasted one
    if (_documentController.text.trim().isNotEmpty) {
      await appState.addDocumentToActiveProject(
        title: '${_titleController.text.trim()} - 30-Day Master Plan',
        content: _documentController.text.trim(),
      );
    }

    // Trigger asynchronous campaign creation
    await appState.create30DayCampaign(
      title: _titleController.text.trim(),
      startDate: _startDate,
      endDate: _endDate,
      platforms: _selectedPlatforms.toList(),
      postingHours: _postingHours,
      rules: configuredRules,
      autoPostingEnabled: _autoPostingEnabled,
      baseTopic: _topicController.text.trim(),
    );

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Campaign created! Generated $_calculatedPostTotal scheduled posts.',
          ),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final appState = context.watch<AppState>();
    final daysCount = _endDate.difference(_startDate).inDays + 1;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Create 30-Day Campaign'),
      ),
      body: Stack(
        children: [
          Form(
            key: _formKey,
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // 1. Campaign Basics
                Text(
                  '1. Campaign Overview',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _titleController,
                  decoration: InputDecoration(
                    labelText: 'Campaign Title',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    prefixIcon: const Icon(Icons.campaign),
                  ),
                  validator: (v) => v == null || v.trim().isEmpty ? 'Enter a title' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _topicController,
                  decoration: InputDecoration(
                    labelText: 'Core Topic / Angle to Rotate Over 30 Days',
                    hintText: 'e.g. B2B Automation, Python Web Dev, Real Estate Tips',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    prefixIcon: const Icon(Icons.psychology),
                  ),
                  validator: (v) => v == null || v.trim().isEmpty ? 'Enter a core topic' : null,
                ),
                const SizedBox(height: 16),
                Text(
                  '30-Day Master Document (Paste here to auto-schedule):',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Paste your complete document with daily topics, benefits, applications, or technologies. The AI will parse Day 1 through Day 30 and schedule 1 post every day at your exact selected time.',
                  style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.outline),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _documentController,
                  maxLines: 5,
                  decoration: InputDecoration(
                    labelText: 'Paste 30-Day Master Document / Plan',
                    hintText: 'Day 1: Topic...\nDay 2: Topic...\nDay 30: Topic...',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    prefixIcon: const Icon(Icons.description_outlined),
                  ),
                ),
                const SizedBox(height: 24),

                // 2. Platform Selection (Modular)
                Text(
                  '2. Target Platforms (Modular)',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Select the platforms where this campaign will publish. Formats will automatically adapt.',
                  style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.outline),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: SocialPlatform.values.map((platform) {
                    final isSelected = _selectedPlatforms.contains(platform);
                    return PlatformBadge(
                      platform: platform,
                      isSelected: isSelected,
                      onTap: () {
                        setState(() {
                          if (isSelected) {
                            if (_selectedPlatforms.length > 1) {
                              _selectedPlatforms.remove(platform);
                            }
                          } else {
                            _selectedPlatforms.add(platform);
                          }
                        });
                      },
                    );
                  }).toList(),
                ),
                const SizedBox(height: 24),

                // 3. Scheduling: Date Range & Times
                Text(
                  '3. Schedule & Cadence ($daysCount Days)',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: InkWell(
                        onTap: _pickStartDate,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                          decoration: BoxDecoration(
                            border: Border.all(color: theme.colorScheme.outlineVariant),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Start Date', style: theme.textTheme.bodySmall),
                              const SizedBox(height: 4),
                              Text(
                                DateFormat('MMM d, yyyy').format(_startDate),
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: InkWell(
                        onTap: _pickEndDate,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                          decoration: BoxDecoration(
                            border: Border.all(color: theme.colorScheme.outlineVariant),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('End Date', style: theme.textTheme.bodySmall),
                              const SizedBox(height: 4),
                              Text(
                                DateFormat('MMM d, yyyy').format(_endDate),
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  'Daily Posting Time Slots (${_postingHours.length} per day):',
                  style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    ..._postingHours.map((hour) {
                      final displayTime = hour == 0
                          ? '12:00 AM'
                          : hour < 12
                              ? '$hour:00 AM'
                              : hour == 12
                                  ? '12:00 PM'
                                  : '${hour - 12}:00 PM';
                      return Chip(
                        label: Text(displayTime),
                        avatar: const Icon(Icons.access_time, size: 16),
                        deleteIcon: const Icon(Icons.close, size: 14),
                        onDeleted: _postingHours.length > 1
                            ? () {
                                setState(() {
                                  _postingHours.remove(hour);
                                });
                              }
                            : null,
                      );
                    }),
                    ActionChip(
                      avatar: const Icon(Icons.add, size: 16),
                      label: const Text('Add Time'),
                      onPressed: _addPostingHour,
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // 4. AI Writing Rules Configuration
                Text(
                  '4. Configure AI Writing Rules',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: _tone,
                  decoration: InputDecoration(
                    labelText: 'Tone & Persona',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  items: _tones.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                  onChanged: (val) => setState(() => _tone = val ?? _tone),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: _hookStyle,
                  decoration: InputDecoration(
                    labelText: 'Hook Style',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  items: _hookStyles
                      .map((h) => DropdownMenuItem(value: h, child: Text(h)))
                      .toList(),
                  onChanged: (val) => setState(() => _hookStyle = val ?? _hookStyle),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: _emojiDensity,
                  decoration: InputDecoration(
                    labelText: 'Emoji Density',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  items: _emojiDensities
                      .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                      .toList(),
                  onChanged: (val) => setState(() => _emojiDensity = val ?? _emojiDensity),
                ),
                const SizedBox(height: 12),
                Text(
                  'Target Hashtags: ${_hashtagCount.round()} per post',
                  style: theme.textTheme.bodyMedium,
                ),
                Slider(
                  value: _hashtagCount,
                  min: 0,
                  max: 8,
                  divisions: 8,
                  label: '${_hashtagCount.round()}',
                  onChanged: (val) => setState(() => _hashtagCount = val),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _ctaController,
                  decoration: InputDecoration(
                    labelText: 'Default Call-To-Action (CTA)',
                    hintText: 'e.g. Leave a comment below with your experience!',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _targetAudienceController,
                  decoration: InputDecoration(
                    labelText: 'Target Audience Profile',
                    hintText: 'e.g. Tech leads, startup founders, solopreneurs',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _customInstructionsController,
                  maxLines: 2,
                  decoration: InputDecoration(
                    labelText: 'Custom Negative Constraints & Rules',
                    hintText: 'e.g. Avoid corporate jargon, write in 1st person, short lines',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
                const SizedBox(height: 24),

                // 5. Automatic Posting Switch
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest.withAlpha(50),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: theme.colorScheme.outlineVariant.withAlpha(60)),
                  ),
                  child: SwitchListTile.adaptive(
                    contentPadding: EdgeInsets.zero,
                    title: const Text(
                      'Enable Automatic Posting',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: const Text(
                      'When enabled, posts in this campaign will automatically publish at scheduled timestamps without manual confirmation.',
                    ),
                    value: _autoPostingEnabled,
                    onChanged: (val) => setState(() => _autoPostingEnabled = val),
                  ),
                ),
                const SizedBox(height: 24),

                // Summary & Submit
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primary.withAlpha(20),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Estimated Output:', style: TextStyle(fontSize: 12)),
                          Text(
                            '$_calculatedPostTotal Total Posts',
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: theme.colorScheme.primary,
                            ),
                          ),
                        ],
                      ),
                      Text(
                        'Across ${_selectedPlatforms.length} Platforms',
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  icon: const Icon(Icons.auto_awesome),
                  label: const Text(
                    'Generate 30-Day Campaign',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: theme.colorScheme.primary,
                    foregroundColor: theme.colorScheme.onPrimary,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  onPressed: appState.isGenerating ? null : _generateCampaign,
                ),
                const SizedBox(height: 40),
              ],
            ),
          ),
          if (appState.isGenerating)
            Container(
              color: Colors.black.withAlpha(150),
              child: Center(
                child: Card(
                  margin: const EdgeInsets.all(32),
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const CircularProgressIndicator(),
                        const SizedBox(height: 20),
                        Text(
                          'Generating 30-Day Campaign...',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Drafting multi-platform hooks and scheduling posts using local AI rules.',
                          textAlign: TextAlign.center,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.outline,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
