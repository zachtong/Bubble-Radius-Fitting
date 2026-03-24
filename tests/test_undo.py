"""Tests for the generic UndoStack."""

from bubbletrack.model.undo import UndoStack


class TestUndoStack:
    def test_push_and_undo(self):
        s = UndoStack()
        s.push("a")
        s.push("b")
        assert s.undo() == "b"
        assert s.undo() == "a"
        assert s.undo() is None

    def test_redo_after_undo(self):
        s = UndoStack()
        s.push("a")
        s.push("b")
        s.undo()
        assert s.redo() == "b"

    def test_push_clears_redo(self):
        s = UndoStack()
        s.push("a")
        s.push("b")
        s.undo()
        s.push("c")
        assert not s.can_redo()

    def test_max_size(self):
        s = UndoStack(max_size=3)
        for i in range(5):
            s.push(i)
        items = []
        while s.can_undo():
            items.append(s.undo())
        assert items == [4, 3, 2]  # oldest (0, 1) evicted

    def test_clear(self):
        s = UndoStack()
        s.push("a")
        s.clear()
        assert not s.can_undo()
        assert not s.can_redo()

    def test_redo_empty(self):
        s = UndoStack()
        assert s.redo() is None

    def test_can_undo_empty(self):
        s = UndoStack()
        assert not s.can_undo()

    def test_can_redo_after_clear(self):
        s = UndoStack()
        s.push("a")
        s.push("b")
        s.undo()
        assert s.can_redo()
        s.clear()
        assert not s.can_redo()

    def test_interleaved_undo_redo(self):
        s = UndoStack()
        s.push("a")
        s.push("b")
        s.push("c")
        assert s.undo() == "c"
        assert s.redo() == "c"
        assert s.undo() == "c"
        assert s.undo() == "b"
        assert s.redo() == "b"
