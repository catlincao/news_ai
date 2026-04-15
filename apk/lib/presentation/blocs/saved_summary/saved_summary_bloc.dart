import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../data/models/saved_summary.dart';
import '../../../data/services/saved_summary_service.dart';
import 'saved_summary_event.dart';
import 'saved_summary_state.dart';

class SavedSummaryBloc extends Bloc<SavedSummaryEvent, SavedSummaryState> {
  final SavedSummaryService _service;

  SavedSummaryBloc({required SavedSummaryService service})
      : _service = service,
        super(const SavedSummaryState()) {
    on<LoadSavedSummaries>(_onLoad);
    on<SaveSummary>(_onSave);
    on<DeleteSavedSummary>(_onDelete);
  }

  void _onLoad(LoadSavedSummaries event, Emitter<SavedSummaryState> emit) {
    emit(state.copyWith(status: SavedSummaryStatus.loading));
    try {
      final summaries = _service.getAll();
      emit(state.copyWith(
        status: SavedSummaryStatus.success,
        summaries: summaries,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: SavedSummaryStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onSave(SaveSummary event, Emitter<SavedSummaryState> emit) async {
    try {
      final now = DateTime.now();
      final title = _service.generateTitle(event.feedIds, now);

      // Check for duplicate
      if (_service.exists(event.feedIds, now)) {
        emit(state.copyWith(
          status: SavedSummaryStatus.failure,
          errorMessage: '该摘要已收藏',
        ));
        return;
      }

      final id = '${now.millisecondsSinceEpoch}';
      final saved = SavedSummary(
        id: id,
        title: title,
        result: event.result,
        feedIds: event.feedIds,
        savedAt: now,
      );
      await _service.save(saved);
      final summaries = _service.getAll();
      emit(state.copyWith(
        status: SavedSummaryStatus.success,
        summaries: summaries,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: SavedSummaryStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onDelete(DeleteSavedSummary event, Emitter<SavedSummaryState> emit) async {
    try {
      await _service.delete(event.id);
      final summaries = _service.getAll();
      emit(state.copyWith(
        status: SavedSummaryStatus.success,
        summaries: summaries,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: SavedSummaryStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }
}
