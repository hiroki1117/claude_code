# テトリスゲーム実行ガイド

## 🎮 メインゲーム実行

### 通常実行（推奨）
```bash
python3 main.py
```

### 実行可能ファイル形式
```bash
./main.py
```

## 📋 実行環境の確認

### 1. ターミナル機能テスト
```bash
python3 test_terminal.py
```
- Pythonバージョン確認
- ターミナルTTY確認
- cursesライブラリテスト
- 色表示対応確認

### 2. 最小限のcursesテスト
```bash
python3 test_curses_minimal.py
```
- curses初期化テスト
- 環境変数確認
- TTY状態確認

## 🎨 代替実行方法

### 視覚デモ版（curses不要）
```bash
python3 visual_test.py
```
- ゲームロジックの動作確認
- 全テトロミノの表示テスト
- 回転機能のデモ
- ANSIカラー対応

### シンプル版（非対話式）
```bash
python3 simple_tetris.py
```
- ANSIエスケープシーケンス使用
- 基本的なテトリス機能
- デバッグ用途

## 🔧 トラブルシューティング

### エラー「Error: Not running in a terminal」
**原因**: TTY環境ではない（IDE内実行など）  
**解決法**: 
```bash
# ターミナルアプリから直接実行
python3 main.py

# または環境確認
python3 test_terminal.py
```

### エラー「Terminal too small」
**原因**: ターミナルサイズ不足  
**要件**: 最小45x25文字  
**解決法**: ターミナルウィンドウを拡大

### エラー「Terminal does not support colors」
**原因**: カラー表示非対応  
**解決法**:
```bash
# 環境変数設定
TERM=xterm-256color python3 main.py

# または別ターミナル使用
# Terminal.app, iTerm2, など
```

### cursesエラー「cbreak() returned ERR」
**原因**: 対話的ターミナル環境ではない  
**解決法**:
```bash
# デモ版を使用
python3 visual_test.py

# または実際のターミナルで実行
```

## 🎯 推奨実行環境

### macOS
```bash
# Terminal.app
python3 main.py

# iTerm2
python3 main.py
```

### Linux
```bash
# gnome-terminal, xterm, konsole等
python3 main.py
```

### Windows
```bash
# Windows Terminal
python main.py

# PowerShell
python main.py
```

## 📊 実行結果の確認

### 正常起動時の表示
```
|..................| Next:
|..................| [][]
|..................| [][]
|..................|
|..................| Score: 0
|..................| Level: 1
|..................| Lines: 0
|..................|
|..................| Controls:
|..................| W/↑: Rotate
|..................| A/←: Left
|..................| D/→: Right
|..................| S/↓: Soft Drop
|..................| Space: Hard Drop
|..................| P: Pause
|..................| Q: Quit
|----------|
```

### 動作確認コマンド
```bash
# ゲームロジック確認
python3 -c "from tetris_game import TetrisGame; print('Game logic OK')"

# テトロミノ確認
python3 -c "from tetromino import Tetromino; t=Tetromino(); print(f'Tetromino: {t.shape_type}')"

# ボード確認
python3 -c "from game_board import GameBoard; b=GameBoard(); print(f'Board: {b.width}x{b.height}')"
```

## ⚡ クイックスタート

```bash
# 1. 環境確認
python3 test_terminal.py

# 2. ゲーム実行
python3 main.py

# 3. エラー時はデモ版
python3 visual_test.py
```

## 🎮 操作方法

| キー | 動作 |
|------|------|
| W / ↑ | 右回転 |
| S / ↓ | ソフトドロップ |
| A / ← | 左移動 |  
| D / → | 右移動 |
| Space | ハードドロップ |
| P | ポーズ/再開 |
| Q | ゲーム終了 |