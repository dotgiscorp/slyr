#!/usr/bin/env python

"""
Converts parsed symbol properties to a Python dictionary
"""

from typing import Union, Optional
from slyr.converters.converter import (
    Converter,
    NotImplementedException
)
from slyr.parser.symbol_parser import (
    Symbol,
    FillSymbol,
    LineSymbol,
    MarkerSymbol
)
from slyr.parser.objects.symbol_layer import SymbolLayer
from slyr.parser.objects.line_symbol_layer import (
    LineSymbolLayer,
    SimpleLineSymbolLayer,
    CartographicLineSymbolLayer,
    MarkerLineSymbolLayer,
    HashLineSymbolLayer
)
from slyr.parser.objects.fill_symbol_layer import (
    SimpleFillSymbolLayer,
    GradientFillSymbolLayer,
    LineFillSymbolLayer,
    MarkerFillSymbolLayer,
    FillSymbolLayer,
    PictureFillSymbolLayer,
    ColorSymbol)
from slyr.parser.objects.marker_symbol_layer import (
    SimpleMarkerSymbolLayer,
    CharacterMarkerSymbolLayer,
    ArrowMarkerSymbolLayer,
    PictureMarkerSymbolLayer
)
from slyr.parser.objects.marker_symbol_layer import MarkerSymbolLayer
from slyr.parser.objects.line_template import LineTemplate
from slyr.parser.objects.decoration import (
    LineDecoration,
    SimpleLineDecoration
)
from slyr.parser.objects.font import Font
from slyr.parser.objects.ramps import ColorRamp
from slyr.parser.objects.picture import (Picture,
                                         BmpPicture,
                                         EmfPicture,
                                         StdPicture)
from slyr.parser.pictures import PictureUtils


class DictionaryConverter(Converter):  # pylint: disable=too-many-public-methods
    """
    Converts symbols to a Python dictionary
    """

    def __init__(self):
        self.out = {}

    def convert_symbol(self, symbol: Symbol):
        self.out = {}
        super().convert_symbol(symbol)
        return self.out

    def convert_fill_symbol(self, symbol: Union[SymbolLayer, FillSymbol]):
        self.out = {
            'type': 'FillSymbol',
            'levels': []
        }
        if issubclass(symbol.__class__, SymbolLayer):
            self.out['levels'].append(self.convert_symbol_layer(symbol))
        else:
            for l in symbol.levels:
                self.out['levels'].append(self.convert_symbol_layer(l))

    def convert_line_symbol(self, symbol: Union[SymbolLayer, LineSymbol]):
        self.out = {
            'type': 'LineSymbol',
            'levels': []
        }
        if issubclass(symbol.__class__, SymbolLayer):
            self.out['levels'].append(self.convert_symbol_layer(symbol))
        else:
            for l in symbol.levels:
                self.out['levels'].append(self.convert_symbol_layer(l))

    def convert_marker_symbol(self, symbol: Union[SymbolLayer, MarkerSymbol]):
        self.out = {
            'type': 'MarkerSymbol',
            'levels': [],
            'halo': symbol.halo,
            'halo_size': symbol.halo_size,
            'halo_symbol_type': type(symbol.halo_symbol).__name__
        }

        if isinstance(symbol.halo_symbol, FillSymbol):
            halo_converter = DictionaryConverter()
            self.out['halo_symbol'] = halo_converter.convert_symbol(symbol.halo_symbol)

        if issubclass(symbol.__class__, SymbolLayer):
            self.out['levels'].append(self.convert_symbol_layer(symbol))
        else:
            for l in symbol.levels:
                self.out['levels'].append(self.convert_symbol_layer(l))

    def convert_symbol_layer(self, layer: SymbolLayer) -> dict:
        """
        Converts a SymbolLayer
        """
        if issubclass(layer.__class__, FillSymbolLayer):
            out = self.convert_fill_symbol_layer(layer)
        elif issubclass(layer.__class__, LineSymbolLayer):
            out = DictionaryConverter.convert_line_symbol_layer(layer)
        elif issubclass(layer.__class__, MarkerSymbolLayer):
            out = DictionaryConverter.convert_marker_symbol_layer(layer)
        else:
            raise NotImplementedException('{} not implemented yet'.format(layer.__class__))
        out['type'] = type(layer).__name__
        out['enabled'] = layer.enabled
        out['locked'] = layer.locked
        if layer.tags:
            out['tags'] = layer.tags
        return out

    def convert_fill_symbol_layer(self, layer: FillSymbolLayer) -> dict:
        """
        Converts a FillSymbolLayer
        """
        if isinstance(layer, SimpleFillSymbolLayer):
            return self.convert_simple_fill_symbol_layer(layer)
        elif isinstance(layer, ColorSymbol):
            return self.convert_color_symbol(layer)
        elif isinstance(layer, GradientFillSymbolLayer):
            return self.convert_gradient_fill_symbol_layer(layer)
        elif isinstance(layer, LineFillSymbolLayer):
            return self.convert_line_fill_symbol_layer(layer)
        elif isinstance(layer, MarkerFillSymbolLayer):
            return self.convert_marker_fill_symbol_layer(layer)
        elif isinstance(layer, PictureFillSymbolLayer):
            return self.convert_picture_fill_symbol_layer(layer)
        else:
            raise NotImplementedException('{} not implemented yet'.format(layer.__class__))

    def convert_simple_fill_symbol_layer(self, layer: SimpleFillSymbolLayer) -> dict:
        """
        Converts a SimpleFillSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
        }

        if layer.outline_layer:
            out['outline_layer'] = self.convert_symbol_layer(layer.outline_layer)
        if layer.outline_symbol:
            outline_converter = DictionaryConverter()
            out['outline_symbol'] = outline_converter.convert_symbol(layer.outline_symbol)

        return out

    @staticmethod
    def convert_gradient_type(gradient_type: int) -> str:
        """
        Converts a gradient type to string
        """
        if gradient_type == GradientFillSymbolLayer.LINEAR:
            return 'linear'
        elif gradient_type == GradientFillSymbolLayer.CIRCULAR:
            return 'circular'
        elif gradient_type == GradientFillSymbolLayer.BUFFERED:
            return 'buffered'
        elif gradient_type == GradientFillSymbolLayer.RECTANGULAR:
            return 'rectangular'
        raise NotImplementedException('Gradient type {} not implemented yet'.format(gradient_type))

    def convert_gradient_fill_symbol_layer(self, layer: GradientFillSymbolLayer) -> dict:
        """
        Converts a GradientFillSymbolLayer
        """
        out = {
        }

        if layer.outline_layer:
            out['outline_layer'] = self.convert_symbol_layer(layer.outline_layer)
        if layer.outline_symbol:
            outline_converter = DictionaryConverter()
            out['outline_symbol'] = outline_converter.convert_symbol(layer.outline_symbol)
        out['ramp'] = layer.ramp.to_dict()
        out['percent'] = layer.percent
        out['angle'] = layer.angle
        out['intervals'] = layer.intervals
        out['gradient_type'] = self.convert_gradient_type(layer.type)

        return out

    def convert_line_fill_symbol_layer(self, layer: LineFillSymbolLayer) -> dict:
        """
        Converts a LineFillSymbolLayer
        """
        out = {
        }

        if layer.outline_layer:
            out['outline_layer'] = self.convert_symbol_layer(layer.outline_layer)
        if layer.outline_symbol:
            outline_converter = DictionaryConverter()
            out['outline_symbol'] = outline_converter.convert_symbol(layer.outline_symbol)
        if issubclass(layer.line.__class__, Symbol):
            line_converter = DictionaryConverter()
            out['line_symbol'] = line_converter.convert_symbol(layer.line)
        else:
            out['line_symbol'] = self.convert_symbol_layer(layer.line)
        out['angle'] = layer.angle
        out['offset'] = layer.offset
        out['separation'] = layer.separation

        return out

    def convert_marker_fill_symbol_layer(self, layer: MarkerFillSymbolLayer) -> dict:
        """
        Converts a MarkerFillSymbolLayer
        """
        out = {
        }

        if layer.outline_layer:
            out['outline_layer'] = self.convert_symbol_layer(layer.outline_layer)
        if layer.outline_symbol:
            outline_converter = DictionaryConverter()
            out['outline_symbol'] = outline_converter.convert_symbol(layer.outline_symbol)
        if issubclass(layer.marker.__class__, Symbol):
            line_converter = DictionaryConverter()
            out['marker'] = line_converter.convert_symbol(layer.marker)
        else:
            out['marker'] = self.convert_symbol_layer(layer.marker)
        out['offset_x'] = layer.offset_x
        out['offset_y'] = layer.offset_y
        out['separation_x'] = layer.separation_x
        out['separation_y'] = layer.separation_y
        out['random'] = layer.random

        return out

    @staticmethod
    def convert_picture(picture: Picture) -> Optional[dict]:
        """
        Converts a picture
        """
        if picture is None:
            return None
        if issubclass(picture.__class__, StdPicture):
            picture = picture.picture
        out = {
            'type': picture.__class__.__name__,
        }

        if issubclass(picture.__class__, BmpPicture):
            out['content'] = PictureUtils.to_base64_png(picture.content)
        elif issubclass(picture.__class__, EmfPicture):
            out['content'] = PictureUtils.to_base64(picture.content)
        else:
            raise NotImplementedException('{} picture conversion not implemented'.format(picture.__class__.__name__))
        return out

    def convert_picture_fill_symbol_layer(self, layer: PictureFillSymbolLayer) -> dict:
        """
        Converts a PictureFillSymbolLayer
        """
        out = {
            'color_foreground': DictionaryConverter.convert_color(layer.color_foreground),
            'color_foreground_model': layer.color_foreground.model if layer.color_foreground else None,
            'color_background': DictionaryConverter.convert_color(layer.color_background),
            'color_background_model': layer.color_background.model,
            'color_transparent': DictionaryConverter.convert_color(layer.color_transparent),
            'color_transparent_model': None if not layer.color_transparent else layer.color_transparent.model,
            'swap_fg_bg': layer.swap_fb_gb,
        }

        if layer.outline_layer:
            out['outline_layer'] = self.convert_symbol_layer(layer.outline_layer)
        if layer.outline_symbol:
            outline_converter = DictionaryConverter()
            out['outline_symbol'] = outline_converter.convert_symbol(layer.outline_symbol)

        out['picture'] = DictionaryConverter.convert_picture(layer.picture)
        out['angle'] = layer.angle
        out['scale_x'] = layer.scale_x
        out['scale_y'] = layer.scale_y
        out['offset_x'] = layer.offset_x
        out['offset_y'] = layer.offset_y
        out['separation_x'] = layer.separation_x
        out['separation_y'] = layer.separation_y
        return out

    def convert_color_symbol(self, layer: ColorSymbol) -> dict:
        """
        Converts a ColorSymbol
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
        }
        return out

    @staticmethod
    def convert_line_symbol_layer(layer: LineSymbolLayer) -> dict:
        """
        Converts a LineSymbolLayer
        """
        if isinstance(layer, SimpleLineSymbolLayer):
            return DictionaryConverter.convert_simple_line_symbol_layer(layer)
        elif isinstance(layer, CartographicLineSymbolLayer):
            return DictionaryConverter.convert_cartographic_line_symbol_layer(layer)
        elif isinstance(layer, HashLineSymbolLayer):
            return DictionaryConverter.convert_hash_line_symbol_layer(layer)
        elif isinstance(layer, MarkerLineSymbolLayer):
            return DictionaryConverter.convert_marker_line_symbol_layer(layer)
        else:
            raise NotImplementedException('{} not implemented yet'.format(layer.__class__))

    @staticmethod
    def convert_decoration(decoration: LineDecoration) -> dict:
        """
        Converts a LineDecoration object
        """
        out = {
            'decorations': []
        }
        for d in decoration.decorations:
            if isinstance(d, LineDecoration):
                marker_converter = DictionaryConverter()
                out['decorations'].append(marker_converter.convert_decoration(d))
            elif isinstance(d, SimpleLineDecoration):
                marker_converter = DictionaryConverter()
                out['decorations'].append(marker_converter.convert_simple_line_decoration(d))
        return out

    @staticmethod
    def convert_simple_line_symbol_layer(layer: SimpleLineSymbolLayer) -> dict:
        """
        Converts a SimpleLineSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'width': layer.width,
            'line_type': layer.line_type
        }
        return out

    @staticmethod
    def convert_simple_line_decoration(layer: SimpleLineDecoration) -> dict:
        """
        Converts a SimpleLineDecoration
        """
        out = {
            'fixed_angle': layer.fixed_angle,
            'flip_first': layer.flip_first,
            'flip_all': layer.flip_all,
            'marker': None,
            'positions': layer.marker_positions
        }

        if isinstance(layer.marker, (SymbolLayer)):
            marker_converter = DictionaryConverter()
            out['marker'] = marker_converter.convert_symbol_layer(layer.marker)
        elif isinstance(layer.marker, (Symbol)):
            marker_converter = DictionaryConverter()
            out['marker'] = marker_converter.convert_symbol(layer.marker)

        return out

    @staticmethod
    def convert_template(template: LineTemplate) -> dict:
        """
        Converts a CartographicLineSymbolLayer
        """
        out = {
            'pattern_interval': template.pattern_interval,
            'pattern_parts': template.pattern_parts
        }
        return out

    @staticmethod
    def convert_cartographic_line_symbol_layer(layer: CartographicLineSymbolLayer) -> dict:
        """
        Converts a CartographicLineSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'width': layer.width,
            'offset': layer.offset,
            'cap': layer.cap,
            'join': layer.join,
            'template': None,
            'decoration': None
        }
        if layer.template is not None:
            converter = DictionaryConverter()
            out['template'] = converter.convert_template(layer.template)

        if layer.decoration is not None:
            if isinstance(layer.decoration, (LineDecoration)):
                marker_converter = DictionaryConverter()
                out['decoration'] = marker_converter.convert_decoration(layer.decoration)
            elif isinstance(layer.decoration, (SimpleLineDecoration)):
                marker_converter = DictionaryConverter()
                out['decoration'] = marker_converter.convert_simple_line_decoration(layer.decoration)

        return out

    @staticmethod
    def convert_marker_line_symbol_layer(layer: MarkerLineSymbolLayer) -> dict:
        """
        Converts a MarkerLineSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model if layer.color else None,
            'offset': layer.offset,
            'cap': layer.cap,
            'join': layer.join,
            'template': None,
            'pattern_marker': None,
            'decoration': None
        }
        if layer.template is not None:
            converter = DictionaryConverter()
            out['template'] = converter.convert_template(layer.template)

        if isinstance(layer.pattern_marker, (SymbolLayer)):
            marker_converter = DictionaryConverter()
            out['pattern_marker'] = marker_converter.convert_symbol_layer(layer.pattern_marker)
        elif isinstance(layer.pattern_marker, (Symbol)):
            marker_converter = DictionaryConverter()
            out['pattern_marker'] = marker_converter.convert_symbol(layer.pattern_marker)

        if layer.decoration is not None:
            if isinstance(layer.decoration, (LineDecoration)):
                marker_converter = DictionaryConverter()
                out['decoration'] = marker_converter.convert_decoration(layer.decoration)
            elif isinstance(layer.decoration, (SimpleLineDecoration)):
                marker_converter = DictionaryConverter()
                out['decoration'] = marker_converter.convert_simple_line_decoration(layer.decoration)

        return out

    @staticmethod
    def convert_hash_line_symbol_layer(layer: HashLineSymbolLayer) -> dict:
        """
        Converts a HashLineSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'width': layer.width,
            'offset': layer.offset,
            'cap': layer.cap,
            'join': layer.join,
            'template': None,
            'decoration': None,
            'line': None
        }
        if layer.template is not None:
            converter = DictionaryConverter()
            out['template'] = converter.convert_template(layer.template)

        if isinstance(layer.line, (SymbolLayer)):
            marker_converter = DictionaryConverter()
            out['line'] = marker_converter.convert_symbol_layer(layer.line)
        elif isinstance(layer.line, (Symbol)):
            marker_converter = DictionaryConverter()
            out['line'] = marker_converter.convert_symbol(layer.line)

        if layer.decoration is not None:
            if isinstance(layer.decoration, (LineDecoration)):
                marker_converter = DictionaryConverter()
                out['decoration'] = marker_converter.convert_decoration(layer.decoration)
            elif isinstance(layer.decoration, (SimpleLineDecoration)):
                marker_converter = DictionaryConverter()
                out['decoration'] = marker_converter.convert_simple_line_decoration(layer.decoration)

        return out

    @staticmethod
    def convert_marker_symbol_layer(layer: MarkerSymbolLayer) -> dict:
        """
        Converts a MarkerSymbolLayer
        """
        if isinstance(layer, SimpleMarkerSymbolLayer):
            return DictionaryConverter.convert_simple_marker_symbol_layer(layer)
        elif isinstance(layer, CharacterMarkerSymbolLayer):
            return DictionaryConverter.convert_character_marker_symbol_layer(layer)
        elif isinstance(layer, ArrowMarkerSymbolLayer):
            return DictionaryConverter.convert_arrow_marker_symbol_layer(layer)
        elif isinstance(layer, PictureMarkerSymbolLayer):
            return DictionaryConverter.convert_picture_marker_symbol_layer(layer)
        else:
            raise NotImplementedException('{} not implemented yet'.format(layer.__class__))

    @staticmethod
    def convert_simple_marker_symbol_layer(layer: SimpleMarkerSymbolLayer) -> dict:
        """
        Converts a SimpleMarkerSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'marker_type': layer.type,
            'size': layer.size,
            'x_offset': layer.x_offset,
            'y_offset': layer.y_offset,
            'outline_enabled': layer.outline_enabled,
            'outline_color_model': layer.outline_color.model,
            'outline_color': layer.outline_color.to_dict(),
            'outline_size': layer.outline_width
        }
        return out

    @staticmethod
    def convert_character_marker_symbol_layer(layer: CharacterMarkerSymbolLayer) -> dict:
        """
        Converts a CharacterMarkerSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'unicode': layer.unicode,
            'font': layer.font,
            'std_font': None,
            'size': layer.size,
            'angle': layer.angle,
            'x_offset': layer.x_offset,
            'y_offset': layer.y_offset
        }
        if layer.std_font is not None:
            out['std_font'] = DictionaryConverter.convert_font(layer.std_font)
        return out

    @staticmethod
    def convert_arrow_marker_symbol_layer(layer: ArrowMarkerSymbolLayer) -> dict:
        """
        Converts a ArrowMarkerSymbolLayer
        """
        out = {
            'color': DictionaryConverter.convert_color(layer.color),
            'color_model': layer.color.model,
            'size': layer.size,
            'width': layer.width,
            'angle': layer.angle,
            'x_offset': layer.x_offset,
            'y_offset': layer.y_offset
        }
        return out

    @staticmethod
    def convert_picture_marker_symbol_layer(layer: PictureMarkerSymbolLayer) -> dict:
        """
        Converts a PictureMarkerSymbolLayer
        """
        out = {'color_foreground': DictionaryConverter.convert_color(layer.color_foreground),
               'color_foreground_model': layer.color_foreground.model,
               'color_background': DictionaryConverter.convert_color(layer.color_background),
               'color_background_model': layer.color_background.model,
               'color_transparent': DictionaryConverter.convert_color(layer.color_transparent),
               'color_transparent_model': None if not layer.color_transparent else layer.color_transparent.model,
               'size': layer.size, 'angle': layer.angle, 'x_offset': layer.x_offset, 'y_offset': layer.y_offset,
               'swap_fg_bg': layer.swap_fb_gb, 'picture': DictionaryConverter.convert_picture(layer.picture)}

        return out

    @staticmethod
    def convert_color(color) -> dict:
        """
        Converts a color
        """
        return color.to_dict() if color is not None else None

    @staticmethod
    def convert_font(font: Font) -> dict:
        """
        Converts a font
        """
        return {'font_name': font.font_name,
                'charset': font.charset,
                'weight': font.weight,
                'size': font.size,
                'italic': font.italic,
                'strikethrough': font.strikethrough,
                'underline': font.underline}

    def convert_color_ramp(self, ramp: ColorRamp):
        self.out = ramp.to_dict()
