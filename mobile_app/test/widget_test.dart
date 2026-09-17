import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile_app/main.dart';
import 'package:mobile_app/services/storage_service.dart';
import 'package:mobile_app/providers/app_state.dart';

class _MockHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..connectionTimeout = const Duration(milliseconds: 100);
  }
}

void main() {
  setUpAll(() {
    HttpOverrides.global = _MockHttpOverrides();
  });

  testWidgets('SocialAiApp smoke test and navigation verify', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    final storage = await StorageService.init();

    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => AppState(storage)),
        ],
        child: const SocialAiApp(),
      ),
    );

    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    // Verify header title and navigation buttons are rendered
    expect(find.text('Social AI Studio'), findsOneWidget);
    expect(find.text('Dashboard'), findsOneWidget);
    expect(find.text('Schedule'), findsOneWidget);
    expect(find.text('Projects'), findsOneWidget);
  });
}
