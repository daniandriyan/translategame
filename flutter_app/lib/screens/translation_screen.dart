import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/models.dart';
import '../widgets/text_list.dart';

class TranslationScreen extends StatefulWidget {
  final ROMInfo romInfo;
  final List<TextEntry> texts;
  final ApiService apiService;

  const TranslationScreen({
    super.key,
    required this.romInfo,
    required this.texts,
    required this.apiService,
  });

  @override
  State<TranslationScreen> createState() => _TranslationScreenState();
}

class _TranslationScreenState extends State<TranslationScreen> {
  late List<TextEntry> _texts;
  bool _isTranslating = false;
  TranslationProgress? _progress;

  @override
  void initState() {
    super.initState();
    _texts = widget.texts;
  }

  Future<void> _startTranslation() async {
    setState(() {
      _isTranslating = true;
    });

    try {
      // Start translation
      await widget.apiService.startTranslation();

      // Poll progress
      await _pollProgress();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Translation error: $e')),
        );
      }
    } finally {
      setState(() {
        _isTranslating = false;
      });
    }
  }

  Future<void> _pollProgress() async {
    while (mounted) {
      try {
        _progress = await widget.apiService.getTranslationProgress();
        setState(() {});

        if (!_progress!.isRunning || _progress!.progress >= 100) {
          break;
        }

        await Future.delayed(const Duration(seconds: 1));
      } catch (e) {
        break;
      }
    }

    // Refresh texts
    if (mounted) {
      _texts = await widget.apiService.getTexts();
      setState(() {});
    }
  }

  Future<void> _exportPatch() async {
    try {
      final path = await widget.apiService.exportPatch();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Patch exported to: $path')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Export error: $e')),
        );
      }
    }
  }

  Future<void> _injectToRom() async {
    try {
      final result = await widget.apiService.injectToRom();
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Injection Complete'),
            content: Text(
              'Injected: ${result['injected']} texts\n'
              'Failed: ${result['failed']} texts\n\n'
              'Saved to: ${result['output_path']}',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Injection error: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final translatedCount = _texts.where((t) => t.isTranslated).length;
    final totalCount = _texts.length;

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.romInfo.gameTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.save),
            tooltip: 'Export Patch',
            onPressed: _exportPatch,
          ),
          IconButton(
            icon: const Icon(Icons.system_update_alt),
            tooltip: 'Inject to ROM',
            onPressed: _injectToRom,
          ),
        ],
      ),
      body: Column(
        children: [
          // ROM Info Card
          Card(
            margin: const EdgeInsets.all(8),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(
                    Icons.videogame_asset,
                    size: 40,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.romInfo.gameTitle,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Chip(
                              label: Text(widget.romInfo.emulatorType.toUpperCase()),
                              padding: EdgeInsets.zero,
                              labelPadding: const EdgeInsets.symmetric(horizontal: 8),
                              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            ),
                            const SizedBox(width: 8),
                            Chip(
                              label: Text(widget.romInfo.region),
                              padding: EdgeInsets.zero,
                              labelPadding: const EdgeInsets.symmetric(horizontal: 8),
                              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              widget.romInfo.fileSizeFormatted,
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Translation Progress or Button
          if (_isTranslating && _progress != null)
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 8),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    LinearProgressIndicator(
                      value: _progress!.progress / 100,
                      minHeight: 8,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(_progress!.progressFormatted),
                        Text(_progress!.countFormatted),
                      ],
                    ),
                  ],
                ),
              ),
            )
          else
            Padding(
              padding: const EdgeInsets.all(8),
              child: Row(
                children: [
                  Expanded(
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          children: [
                            Text(
                              '$translatedCount',
                              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                    color: Colors.green,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                            const Text('Translated'),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          children: [
                            Text(
                              '${totalCount - translatedCount}',
                              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                    color: Colors.orange,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                            const Text('Pending'),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),

          // Translate Button
          if (!_isTranslating && translatedCount < totalCount)
            Padding(
              padding: const EdgeInsets.all(8),
              child: ElevatedButton.icon(
                onPressed: _startTranslation,
                icon: const Icon(Icons.translate),
                label: const Text('Start Translation'),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
            ),

          // Divider
          const Divider(),

          // Text List
          Expanded(
            child: TextList(
              texts: _texts,
              onTextUpdated: (index, newText) async {
                await widget.apiService.updateText(index, newText);
                setState(() {
                  _texts[index].translated = newText;
                  _texts[index].isTranslated = true;
                });
              },
            ),
          ),
        ],
      ),
    );
  }
}
