import 'package:flutter/material.dart';
import '../models/models.dart';

class TextList extends StatefulWidget {
  final List<TextEntry> texts;
  final Function(int index, String newText) onTextUpdated;

  const TextList({
    super.key,
    required this.texts,
    required this.onTextUpdated,
  });

  @override
  State<TextList> createState() => _TextListState();
}

class _TextListState extends State<TextList> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  String _filterStatus = 'all'; // all, translated, pending

  List<TextEntry> get _filteredTexts {
    return widget.texts.where((text) {
      // Filter by search
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        if (!text.original.toLowerCase().contains(query) &&
            !text.translated.toLowerCase().contains(query)) {
          return false;
        }
      }

      // Filter by status
      if (_filterStatus == 'translated' && !text.isTranslated) return false;
      if (_filterStatus == 'pending' && text.isTranslated) return false;

      return true;
    }).toList();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Search and Filter Bar
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Column(
            children: [
              // Search box
              TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Search texts...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: _searchQuery.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            setState(() {
                              _searchController.clear();
                              _searchQuery = '';
                            });
                          },
                        )
                      : null,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                ),
                onChanged: (value) {
                  setState(() {
                    _searchQuery = value;
                  });
                },
              ),
              const SizedBox(height: 8),

              // Filter chips
              Row(
                children: [
                  _buildFilterChip('All', 'all', Icons.list),
                  const SizedBox(width: 8),
                  _buildFilterChip('Translated', 'translated', Icons.check_circle),
                  const SizedBox(width: 8),
                  _buildFilterChip('Pending', 'pending', Icons.pending),
                ],
              ),
            ],
          ),
        ),

        // Text List
        Expanded(
          child: ListView.builder(
            itemCount: _filteredTexts.length,
            itemBuilder: (context, index) {
              final text = _filteredTexts[index];
              final originalIndex = widget.texts.indexOf(text);

              return _buildTextItem(originalIndex, text);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildFilterChip(String label, String value, IconData icon) {
    final isSelected = _filterStatus == value;
    return FilterChip(
      selected: isSelected,
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16),
          const SizedBox(width: 4),
          Text(label),
        ],
      ),
      onSelected: (selected) {
        setState(() {
          _filterStatus = value;
        });
      },
    );
  }

  Widget _buildTextItem(int index, TextEntry text) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: ExpansionTile(
        leading: Icon(
          text.isTranslated ? Icons.check_circle : Icons.radio_button_unchecked,
          color: text.isTranslated ? Colors.green : Colors.grey,
        ),
        title: Text(
          text.original,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: text.isTranslated
            ? Text(
                text.translated,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.primary,
                ),
              )
            : const Text(
                'Not translated yet',
                style: TextStyle(fontStyle: FontStyle.italic),
              ),
        trailing: text.needsReview
            ? const Icon(Icons.warning, color: Colors.orange)
            : null,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Original text
                const Text(
                  'Original:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: SelectableText(text.original),
                ),
                const SizedBox(height: 16),

                // Translation (editable)
                const Text(
                  'Translation:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                TextField(
                  controller: TextEditingController(text: text.translated),
                  decoration: InputDecoration(
                    hintText: 'Enter translation...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.save),
                      onPressed: () {
                        // Save will be handled by onSubmitted
                      },
                    ),
                  ),
                  maxLines: null,
                  onSubmitted: (newValue) {
                    widget.onTextUpdated(index, newValue);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Translation saved'),
                        duration: Duration(seconds: 1),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
