import abc
from collections.abc import Generator

from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib._animation_data import DISPLAY_TEMPLATE as DISPLAY_TEMPLATE
from matplotlib._animation_data import INCLUDED_FRAMES as INCLUDED_FRAMES
from matplotlib._animation_data import JS_INCLUDE as JS_INCLUDE
from matplotlib._animation_data import STYLE_INCLUDE as STYLE_INCLUDE

subprocess_creation_flags: Incomplete

def adjusted_figsize(w, h, dpi, n): ...

class MovieWriterRegistry:
    def __init__(self) -> None: ...
    def register(self, name): ...
    def is_available(self, name): ...
    def __iter__(self): ...
    def list(self): ...
    def __getitem__(self, name): ...

writers: Incomplete

class AbstractMovieWriter(abc.ABC, metaclass=abc.ABCMeta):
    fps: Incomplete
    metadata: Incomplete
    codec: Incomplete
    bitrate: Incomplete
    def __init__(
        self,
        fps: int = 5,
        metadata: Incomplete | None = None,
        codec: Incomplete | None = None,
        bitrate: Incomplete | None = None,
    ) -> None: ...
    outfile: Incomplete
    fig: Incomplete
    dpi: Incomplete
    @abc.abstractmethod
    def setup(self, fig, outfile, dpi: Incomplete | None = None): ...
    @property
    def frame_size(self): ...
    @abc.abstractmethod
    def grab_frame(self, **savefig_kwargs): ...
    @abc.abstractmethod
    def finish(self): ...
    def saving(
        self, fig, outfile, dpi, *args, **kwargs
    ) -> Generator[Incomplete, None, None]: ...

class MovieWriter(AbstractMovieWriter):
    supported_formats: Incomplete
    frame_format: Incomplete
    extra_args: Incomplete
    def __init__(
        self,
        fps: int = 5,
        codec: Incomplete | None = None,
        bitrate: Incomplete | None = None,
        extra_args: Incomplete | None = None,
        metadata: Incomplete | None = None,
    ) -> None: ...
    def setup(self, fig, outfile, dpi: Incomplete | None = None) -> None: ...
    def finish(self) -> None: ...
    def grab_frame(self, **savefig_kwargs) -> None: ...
    @classmethod
    def bin_path(cls): ...
    @classmethod
    def isAvailable(cls): ...

class FileMovieWriter(MovieWriter):
    def __init__(self, *args, **kwargs) -> None: ...
    fig: Incomplete
    outfile: Incomplete
    dpi: Incomplete
    temp_prefix: Incomplete
    fname_format_str: str
    def setup(
        self,
        fig,
        outfile,
        dpi: Incomplete | None = None,
        frame_prefix: Incomplete | None = None,
    ) -> None: ...
    def __del__(self) -> None: ...
    @property
    def frame_format(self): ...
    @frame_format.setter
    def frame_format(self, frame_format) -> None: ...
    def grab_frame(self, **savefig_kwargs) -> None: ...
    def finish(self) -> None: ...

class PillowWriter(AbstractMovieWriter):
    @classmethod
    def isAvailable(cls): ...
    def setup(self, fig, outfile, dpi: Incomplete | None = None) -> None: ...
    def grab_frame(self, **savefig_kwargs) -> None: ...
    def finish(self) -> None: ...

class FFMpegBase:
    codec: str
    @property
    def output_args(self): ...

class FFMpegWriter(FFMpegBase, MovieWriter): ...

class FFMpegFileWriter(FFMpegBase, FileMovieWriter):
    supported_formats: Incomplete

class ImageMagickBase:
    @classmethod
    def bin_path(cls): ...
    @classmethod
    def isAvailable(cls): ...

class ImageMagickWriter(ImageMagickBase, MovieWriter):
    input_names: str

class ImageMagickFileWriter(ImageMagickBase, FileMovieWriter):
    supported_formats: Incomplete
    input_names: Incomplete

class HTMLWriter(FileMovieWriter):
    supported_formats: Incomplete
    @classmethod
    def isAvailable(cls): ...
    embed_frames: Incomplete
    default_mode: Incomplete
    def __init__(
        self,
        fps: int = 30,
        codec: Incomplete | None = None,
        bitrate: Incomplete | None = None,
        extra_args: Incomplete | None = None,
        metadata: Incomplete | None = None,
        embed_frames: bool = False,
        default_mode: str = "loop",
        embed_limit: Incomplete | None = None,
    ) -> None: ...
    def setup(
        self,
        fig,
        outfile,
        dpi: Incomplete | None = None,
        frame_dir: Incomplete | None = None,
    ) -> None: ...
    def grab_frame(self, **savefig_kwargs): ...
    def finish(self) -> None: ...

class Animation:
    frame_seq: Incomplete
    event_source: Incomplete
    def __init__(
        self, fig, event_source: Incomplete | None = None, blit: bool = False
    ) -> None: ...
    def __del__(self) -> None: ...
    def save(
        self,
        filename,
        writer: Incomplete | None = None,
        fps: Incomplete | None = None,
        dpi: Incomplete | None = None,
        codec: Incomplete | None = None,
        bitrate: Incomplete | None = None,
        extra_args: Incomplete | None = None,
        metadata: Incomplete | None = None,
        extra_anim: Incomplete | None = None,
        savefig_kwargs: Incomplete | None = None,
        *,
        progress_callback: Incomplete | None = None,
    ): ...
    def new_frame_seq(self): ...
    def new_saved_frame_seq(self): ...
    def to_html5_video(self, embed_limit: Incomplete | None = None): ...
    def to_jshtml(
        self,
        fps: Incomplete | None = None,
        embed_frames: bool = True,
        default_mode: Incomplete | None = None,
    ): ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...

class TimedAnimation(Animation):
    def __init__(
        self,
        fig,
        interval: int = 200,
        repeat_delay: int = 0,
        repeat: bool = True,
        event_source: Incomplete | None = None,
        *args,
        **kwargs,
    ) -> None: ...

class ArtistAnimation(TimedAnimation):
    def __init__(self, fig, artists, *args, **kwargs) -> None: ...

class FuncAnimation(TimedAnimation):
    def __init__(
        self,
        fig,
        func,
        frames: Incomplete | None = None,
        init_func: Incomplete | None = None,
        fargs: Incomplete | None = None,
        save_count: Incomplete | None = None,
        *,
        cache_frame_data: bool = True,
        **kwargs,
    ) -> None: ...
    def new_frame_seq(self): ...
    def new_saved_frame_seq(self): ...
