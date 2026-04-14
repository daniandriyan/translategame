/// Models untuk Translation App
class ROMInfo {
  final String gameTitle;
  final String emulatorType;
  final String region;
  final int fileSize;
  final String fileName;

  ROMInfo({
    required this.gameTitle,
    required this.emulatorType,
    required this.region,
    required this.fileSize,
    required this.fileName,
  });

  factory ROMInfo.fromJson(Map<String, dynamic> json) {
    return ROMInfo(
      gameTitle: json['game_title'] ?? 'Unknown',
      emulatorType: json['emulator_type'] ?? 'unknown',
      region: json['region'] ?? '?',
      fileSize: json['file_size'] ?? 0,
      fileName: json['file_name'] ?? 'unknown',
    );
  }

  String get fileSizeFormatted {
    if (fileSize < 1024 * 1024) {
      return '${(fileSize / 1024).toStringAsFixed(2)} KB';
    }
    return '${(fileSize / (1024 * 1024)).toStringAsFixed(2)} MB';
  }
}

class TextEntry {
  final String original;
  String translated;
  final int offset;
  bool isTranslated;
  bool needsReview;

  TextEntry({
    required this.original,
    this.translated = '',
    required this.offset,
    this.isTranslated = false,
    this.needsReview = false,
  });

  factory TextEntry.fromJson(Map<String, dynamic> json) {
    return TextEntry(
      original: json['original'] ?? '',
      translated: json['translated'] ?? '',
      offset: json['offset'] ?? 0,
      isTranslated: json['is_translated'] ?? false,
      needsReview: json['needs_review'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'original': original,
      'translated': translated,
      'offset': offset,
      'is_translated': isTranslated,
      'needs_review': needsReview,
    };
  }
}

class TranslationProgress {
  final bool isRunning;
  final int total;
  final int translated;
  final double progress;

  TranslationProgress({
    required this.isRunning,
    required this.total,
    required this.translated,
    required this.progress,
  });

  factory TranslationProgress.fromJson(Map<String, dynamic> json) {
    return TranslationProgress(
      isRunning: json['is_running'] ?? false,
      total: json['total'] ?? 0,
      translated: json['translated'] ?? 0,
      progress: (json['progress'] ?? 0).toDouble(),
    );
  }

  String get progressFormatted => '${progress.toStringAsFixed(1)}%';
  String get countFormatted => '$translated/$total texts';
}
