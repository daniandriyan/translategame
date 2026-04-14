import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/models.dart';

class ApiService {
  final String baseUrl;

  ApiService({this.baseUrl = 'http://127.0.0.1:8000'});

  // Health check
  Future<bool> checkConnection() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/'),
      ).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // Get status
  Future<Map<String, dynamic>> getStatus() async {
    final response = await http.get(Uri.parse('$baseUrl/api/status'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to get status');
  }

  // Upload ROM
  Future<ROMInfo> uploadRom(List<int> fileBytes, String fileName) async {
    var uri = Uri.parse('$baseUrl/api/rom/upload');
    var request = http.MultipartRequest('POST', uri);
    
    request.files.add(http.MultipartFile.fromBytes(
      'file',
      fileBytes,
      filename: fileName,
    ));

    var response = await request.send();
    var responseBody = await response.stream.bytesToString();

    if (response.statusCode == 200) {
      var data = json.decode(responseBody);
      return ROMInfo.fromJson(data['rom_info']);
    }
    throw Exception('Failed to upload ROM: $responseBody');
  }

  // Extract texts
  Future<List<TextEntry>> extractTexts() async {
    final response = await http.post(Uri.parse('$baseUrl/api/rom/extract'));
    if (response.statusCode == 200) {
      var data = json.decode(response.body);
      List<dynamic> textsJson = data['texts'] ?? [];
      return textsJson.map((json) => TextEntry.fromJson(json)).toList();
    }
    throw Exception('Failed to extract texts');
  }

  // Start translation
  Future<bool> startTranslation() async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/translate'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'source_lang': 'auto',
        'target_lang': 'Indonesian',
      }),
    );
    return response.statusCode == 200;
  }

  // Get translation progress
  Future<TranslationProgress> getTranslationProgress() async {
    final response = await http.get(Uri.parse('$baseUrl/api/translate/progress'));
    if (response.statusCode == 200) {
      return TranslationProgress.fromJson(json.decode(response.body));
    }
    throw Exception('Failed to get progress');
  }

  // Get all texts
  Future<List<TextEntry>> getTexts() async {
    final response = await http.get(Uri.parse('$baseUrl/api/texts'));
    if (response.statusCode == 200) {
      var data = json.decode(response.body);
      List<dynamic> textsJson = data['texts'] ?? [];
      return textsJson.map((json) => TextEntry.fromJson(json)).toList();
    }
    throw Exception('Failed to get texts');
  }

  // Update single text
  Future<bool> updateText(int index, String translatedText) async {
    final response = await http.put(
      Uri.parse('$baseUrl/api/texts/$index'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'index': index,
        'translated_text': translatedText,
      }),
    );
    return response.statusCode == 200;
  }

  // Export patch
  Future<String> exportPatch({String format = 'json'}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/export'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'format': format,
      }),
    );
    if (response.statusCode == 200) {
      var data = json.decode(response.body);
      return data['output_path'] ?? '';
    }
    throw Exception('Failed to export patch');
  }

  // Inject to ROM
  Future<Map<String, dynamic>> injectToRom() async {
    final response = await http.post(Uri.parse('$baseUrl/api/inject'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to inject to ROM');
  }

  // Save project
  Future<String> saveProject() async {
    final response = await http.post(Uri.parse('$baseUrl/api/project/save'));
    if (response.statusCode == 200) {
      var data = json.decode(response.body);
      return data['output_path'] ?? '';
    }
    throw Exception('Failed to save project');
  }
}
