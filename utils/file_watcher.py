import os
import time
import threading
from typing import Callable, Optional

from utils.logger_handler import logger

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileDeletedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logger.warning("watchdog 未安装，文件监听功能不可用。请执行: pip install watchdog")


class _KnowledgeFileHandler(FileSystemEventHandler):
    """监听 data/ 目录下的文件变更，触发增量索引"""

    def __init__(self, callback: Callable[[str, str], None], allowed_extensions: tuple = (".txt", ".pdf", ".md")):
        super().__init__()
        self.callback = callback
        self.allowed_extensions = allowed_extensions
        self._debounce: dict[str, float] = {}

    def _should_process(self, path: str) -> bool:
        if not path.endswith(self.allowed_extensions):
            return False
        filename = os.path.basename(path)
        if filename.startswith(".") or filename == "md5.txt":
            return False
        now = time.time()
        last = self._debounce.get(path, 0)
        if now - last < 2:
            return False
        self._debounce[path] = now
        return True

    def on_created(self, event):
        if isinstance(event, FileCreatedEvent) and self._should_process(event.src_path):
            logger.info(f"[FileWatcher] 检测到新文件: {event.src_path}")
            self.callback("created", event.src_path)

    def on_deleted(self, event):
        if isinstance(event, FileDeletedEvent) and self._should_process(event.src_path):
            logger.info(f"[FileWatcher] 检测到文件删除: {event.src_path}")
            self.callback("deleted", event.src_path)


class FileWatcher:
    """
    文件变更监听器

    Phase 2.3: 知识库实时更新
    - 监听 data/ 目录变更
    - 新文件自动触发增量索引
    - 文件删除时标记
    """

    def __init__(self):
        self._observer: Optional[Observer] = None
        self._running = False

    def start(self, watch_dir: str, callback: Callable[[str, str], None], extensions: tuple = (".txt", ".pdf", ".md")):
        if not WATCHDOG_AVAILABLE:
            logger.warning("[FileWatcher] watchdog 不可用，跳过文件监听")
            return

        if self._running:
            return

        if not os.path.isdir(watch_dir):
            logger.warning(f"[FileWatcher] 目录不存在: {watch_dir}")
            return

        handler = _KnowledgeFileHandler(callback, extensions)
        self._observer = Observer()
        self._observer.schedule(handler, watch_dir, recursive=True)
        self._observer.daemon = True
        self._observer.start()
        self._running = True
        logger.info(f"[FileWatcher] 开始监听目录: {watch_dir}")

    def stop(self):
        if self._observer and self._running:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._running = False
            logger.info("[FileWatcher] 停止监听")

    @property
    def is_running(self) -> bool:
        return self._running


file_watcher = FileWatcher()
