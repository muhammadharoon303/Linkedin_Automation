import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../core/models/project.dart';
import '../core/models/content_document.dart';
import '../core/models/campaign.dart';
import '../core/models/scheduled_post.dart';
import '../core/models/ai_rules.dart';
import '../core/models/platform_type.dart';
import '../services/storage_service.dart';
import '../services/api_service.dart';
import '../services/campaign_generator_service.dart';

class AppState extends ChangeNotifier {
  final StorageService _storage;
  late ApiService _apiService;
  late CampaignGeneratorService _campaignGenerator;
  final Uuid _uuid = const Uuid();

  List<Project> _projects = [];
  Project? _activeProject;
  List<Campaign> _campaigns = [];
  List<ScheduledPost> _posts = [];
  bool _autoPostingMasterSwitch = true;
  bool _isGenerating = false;
  String _backendStatus = 'checking';
  String _backendUrl = 'http://10.0.2.2:8000';
  String _ollamaModel = 'llama3';
  List<String> _availableModels = ['llama3', 'mistral', 'phi3'];

  AppState(this._storage) {
    _loadFromStorage();
  }

  // Getters
  List<Project> get projects => _projects;
  Project? get activeProject => _activeProject;
  List<Campaign> get campaigns => _campaigns;
  List<ScheduledPost> get posts => _posts;
  bool get autoPostingMasterSwitch => _autoPostingMasterSwitch;
  bool get isGenerating => _isGenerating;
  String get backendStatus => _backendStatus;
  String get backendUrl => _backendUrl;
  String get ollamaModel => _ollamaModel;
  List<String> get availableModels => _availableModels;
  ApiService get apiService => _apiService;

  // Filtered queries
  List<ScheduledPost> get activeProjectPosts {
    if (_activeProject == null) return _posts;
    return _posts.where((p) => p.projectId == _activeProject!.id).toList();
  }

  int get publishedCount => _posts.where((p) => p.status == PostStatus.published).length;
  int get scheduledCount => _posts.where((p) => p.status == PostStatus.scheduled).length;
  int get draftCount => _posts.where((p) => p.status == PostStatus.draft).length;
  int get failedCount => _posts.where((p) => p.status == PostStatus.failed).length;

  void _loadFromStorage() {
    _backendUrl = _storage.getBackendUrl();
    _ollamaModel = _storage.getOllamaModel();
    _apiService = ApiService(baseUrl: _backendUrl);
    _campaignGenerator = CampaignGeneratorService(_apiService);

    _projects = _storage.loadProjects();
    _campaigns = _storage.loadCampaigns();
    _posts = _storage.loadPosts();

    final activeId = _storage.getActiveProjectId();
    if (activeId != null && _projects.any((p) => p.id == activeId)) {
      _activeProject = _projects.firstWhere((p) => p.id == activeId);
    } else if (_projects.isNotEmpty) {
      _activeProject = _projects.first;
    }

    checkBackendHealth();
    notifyListeners();
  }

  List<Map<String, dynamic>> _connectedAccounts = [];
  List<Map<String, dynamic>> get connectedAccounts => _connectedAccounts;

  Future<void> checkBackendHealth() async {
    _backendStatus = 'checking';
    notifyListeners();

    final health = await _apiService.checkHealth();
    if (health['status'] == 'ok' || health['status'] == 'healthy') {
      _backendStatus = 'online';
      final models = await _apiService.fetchAvailableModels();
      if (models.isNotEmpty) _availableModels = models;
      _autoPostingMasterSwitch = await _apiService.getMasterSwitch();
      _connectedAccounts = await _apiService.fetchConnectedAccounts();
    } else {
      _backendStatus = 'offline';
    }
    notifyListeners();
  }

  Future<void> refreshConnectedAccounts() async {
    if (_backendStatus == 'online') {
      _connectedAccounts = await _apiService.fetchConnectedAccounts();
      notifyListeners();
    }
  }

  Future<void> disconnectSocialAccount(String id) async {
    await _apiService.disconnectAccount(id);
    _connectedAccounts.removeWhere((a) => a['id'] == id);
    notifyListeners();
  }

  Future<void> setBackendUrl(String url) async {
    _backendUrl = url;
    await _storage.saveBackendUrl(url);
    _apiService = ApiService(baseUrl: url);
    _campaignGenerator = CampaignGeneratorService(_apiService);
    await checkBackendHealth();
  }

  Future<void> setOllamaModel(String model) async {
    _ollamaModel = model;
    await _storage.saveOllamaModel(model);
    notifyListeners();
  }

  Future<void> setActiveProject(Project project) async {
    _activeProject = project;
    await _storage.saveActiveProjectId(project.id);
    notifyListeners();
  }

  Future<void> createProject({
    required String name,
    required String description,
    required AiWritingRules rules,
  }) async {
    final now = DateTime.now();
    final newProject = Project(
      id: _uuid.v4(),
      name: name,
      description: description,
      defaultAiRules: rules,
      documents: [],
      createdAt: now,
      updatedAt: now,
    );

    _projects.insert(0, newProject);
    _activeProject = newProject;
    await _storage.saveProjects(_projects);
    await _storage.saveActiveProjectId(newProject.id);
    notifyListeners();
  }

  Future<void> updateActiveProjectRules(AiWritingRules rules) async {
    if (_activeProject == null) return;
    final updated = _activeProject!.copyWith(
      defaultAiRules: rules,
      updatedAt: DateTime.now(),
    );
    final index = _projects.indexWhere((p) => p.id == updated.id);
    if (index != -1) {
      _projects[index] = updated;
      _activeProject = updated;
      await _storage.saveProjects(_projects);
      notifyListeners();
    }
  }

  Future<void> addDocumentToActiveProject({
    required String title,
    required String content,
    String? sourcePath,
  }) async {
    if (_activeProject == null) return;
    final wordCount = content.trim().split(RegExp(r'\s+')).where((s) => s.isNotEmpty).length;
    final newDoc = ContentDocument(
      id: _uuid.v4(),
      projectId: _activeProject!.id,
      title: title,
      content: content,
      sourcePath: sourcePath,
      wordCount: wordCount,
      addedAt: DateTime.now(),
    );

    final updatedDocs = List<ContentDocument>.from(_activeProject!.documents)..add(newDoc);
    final updated = _activeProject!.copyWith(
      documents: updatedDocs,
      updatedAt: DateTime.now(),
    );

    final index = _projects.indexWhere((p) => p.id == updated.id);
    if (index != -1) {
      _projects[index] = updated;
      _activeProject = updated;
      await _storage.saveProjects(_projects);
      notifyListeners();
    }
  }

  Future<void> removeDocument(String docId) async {
    if (_activeProject == null) return;
    final updatedDocs = _activeProject!.documents.where((d) => d.id != docId).toList();
    final updated = _activeProject!.copyWith(
      documents: updatedDocs,
      updatedAt: DateTime.now(),
    );

    final index = _projects.indexWhere((p) => p.id == updated.id);
    if (index != -1) {
      _projects[index] = updated;
      _activeProject = updated;
      await _storage.saveProjects(_projects);
      notifyListeners();
    }
  }

  Future<void> toggleAutoPosting(bool value) async {
    _autoPostingMasterSwitch = value;
    notifyListeners();
    if (_backendStatus == 'online') {
      await _apiService.setMasterSwitch(value);
    }
  }

  /// Creates and generates a full 30-day campaign with post scheduling
  Future<void> create30DayCampaign({
    required String title,
    required DateTime startDate,
    required DateTime endDate,
    required List<SocialPlatform> platforms,
    required List<int> postingHours,
    required AiWritingRules rules,
    required bool autoPostingEnabled,
    String? baseTopic,
  }) async {
    if (_activeProject == null) return;
    _isGenerating = true;
    notifyListeners();

    try {
      final result = await _campaignGenerator.generate30DayCampaign(
        project: _activeProject!,
        campaignTitle: title,
        startDate: startDate,
        endDate: endDate,
        platforms: platforms,
        postingHours: postingHours,
        rules: rules,
        autoPostingEnabled: autoPostingEnabled,
        baseTopic: baseTopic,
        model: _ollamaModel,
      );

      _campaigns.insert(0, result.campaign);
      _posts.insertAll(0, result.posts);

      await _storage.saveCampaigns(_campaigns);
      await _storage.savePosts(_posts);
    } finally {
      _isGenerating = false;
      notifyListeners();
    }
  }

  Future<void> updatePost(ScheduledPost updatedPost) async {
    final index = _posts.indexWhere((p) => p.id == updatedPost.id);
    if (index != -1) {
      _posts[index] = updatedPost;
      await _storage.savePosts(_posts);
      notifyListeners();
    }
  }

  Future<void> deletePost(String postId) async {
    _posts.removeWhere((p) => p.id == postId);
    await _storage.savePosts(_posts);
    notifyListeners();
  }

  /// Simulates or executes immediate publication of a post
  Future<void> publishPostNow(String postId) async {
    final index = _posts.indexWhere((p) => p.id == postId);
    if (index == -1) return;

    final current = _posts[index];
    final updated = current.copyWith(
      status: PostStatus.published,
      publishedAt: DateTime.now(),
    );

    _posts[index] = updated;
    await _storage.savePosts(_posts);
    notifyListeners();
  }
}
