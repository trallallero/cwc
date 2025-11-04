"""Plugin module to export crossword in pdf."""

import os
import sys
import inspect

from fpdf import FPDF
from PIL import (
    Image,
    ImageFont,
    ImageDraw
)

current = os.path.dirname(os.path.realpath(__file__))
parent  = os.path.dirname(current)
sys.path.append(parent)

from cwc_globals import (
    GlobalData,
    Direction
)
from word import get_words_by_coord
from cwc_matrix import (
    MatrixType,
    CwcMatrix
)


class PdfExporter:
    """Class to export crossword in pdf."""

    def __init__(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.data        = []
        self.orientation = 'P'

    def export(self, filename):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        try:
            pdf = FPDF()

            im = self.__add_empty_crossword_to_pdf(pdf=pdf)
            self.__add_definitions_to_pdf         (pdf=pdf)
            self.__add_solution_to_pdf            (pdf=pdf, im=im)

            pdf.output(filename)
        except Exception as e:
            raise e

    def test(self):
        pass # TODO

    def __add_empty_crossword_to_pdf(self, pdf:FPDF):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        im  = self.__create_crossword_image()

        width, height = self.__get_info(im=im)

        pdf.add_page(orientation=self.orientation)
        pdf.image(im, x=5, y=5, w=width, h=height)
        return im

    def __add_definitions_to_pdf(self, pdf:FPDF):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        pdf.add_page(orientation=self.orientation)
        pdf.set_font(GlobalData.CURRENT_FONT_NAME, 'B', 12)
        pdf.write(h=5, text='Orizzontali\n')
        for d in self.data:
            if d[0] == 'H':
                pdf.set_font(GlobalData.CURRENT_FONT_NAME, 'B', 10)
                pdf.write(h=5, text=f'{d[1]}. ')
                pdf.set_font(GlobalData.CURRENT_FONT_NAME, '', 10)
                pdf.write(h=5, text=f'{d[2]} - ')

        pdf.set_font(GlobalData.CURRENT_FONT_NAME, 'B', 12)
        pdf.write(h=10, text='\n')
        pdf.write(h=5, text='Verticali\n')
        for d in self.data:
            if d[0] == 'V':
                pdf.set_font(GlobalData.CURRENT_FONT_NAME, 'B', 10)
                pdf.write(h=5, text=f'{d[1]}. ')
                pdf.set_font(GlobalData.CURRENT_FONT_NAME, '', 10)
                pdf.write(h=5, text=f'{d[2]} - ')

    def __add_solution_to_pdf(self, pdf:FPDF, im):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        self.__add_solution_to_image(im=im)

        width, height  = self.__get_info(im=im)

        pdf.add_page(orientation=self.orientation)
        pdf.image(im, x=5, y=5, w=width, h=height)

    def __create_crossword_image(self):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        im   = Image.new(mode="RGB", size=(GlobalData.TOT_COLS*50+2, GlobalData.TOT_ROWS*50+2), color='white')
        draw = ImageDraw.Draw(im)

        for y in range(GlobalData.TOT_ROWS):
            for x in range(GlobalData.TOT_COLS):
                draw.rectangle(((x*50, y*50), (x*50 + 50, y*50 + 50)), fill='white', outline='black')
                if not CwcMatrix.get(matrix_type=MatrixType.BOOLEAN, y=y, x=x):
                    draw.rectangle(((x*50+4, y*50+4), (x*50 + 46, y*50 + 46)), fill='black', outline='black')

                num_lbl = CwcMatrix.get(matrix_type=MatrixType.NUMBER, y=y, x=x)
                if not num_lbl:
                    continue
                words = get_words_by_coord(coord=(y, x))
                for w in words:
                    self.data.append(
                        (
                            'H' if w.get_direction() == Direction.HORIZONTAL else 'V',
                            num_lbl['text'],
                            w.get_current_definition()
                        )
                    )

                if num_lbl['text'] != '':
                    draw.text(
                        xy   = (x*50+5, y*50+5),
                        text = num_lbl['text'],
                        font = ImageFont.truetype(font=GlobalData.EXPORTER_FONT_NAME, size=GlobalData.FONT_SMALL_SIZE),
                        fill = "black")
        return im

    def __add_solution_to_image(self, im):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        draw = ImageDraw.Draw(im)

        for y in range(GlobalData.TOT_ROWS):
            for x in range(GlobalData.TOT_COLS):
                c = CwcMatrix.get_variable_value(y=y, x=x)
                if c:
                    draw.text(
                        xy   = (x*50+20, y*50+20),
                        text = c,
                        font = ImageFont.truetype(font=GlobalData.EXPORTER_FONT_NAME, size=GlobalData.FONT_BIG_SIZE),
                        fill = "black"
                    )
        return im

    def __get_info(self, im):
        print(f'{os.path.basename(inspect.stack()[0][1])} - {inspect.stack()[0][3]}')

        width, height = im.size
        width, height = float(width * 0.264583), float(height * 0.264583)

        # given we are working with A4 format size
        pdf_size = {'P': {'w': 210, 'h': 297}, 'L': {'w': 297, 'h': 210}}

        # get page orientation from image size
        self.orientation = 'P' if width < height else 'L'

        #  make sure image size is not greater than the pdf format size
        width  = width  if width  < pdf_size[self.orientation]['w'] else pdf_size[self.orientation]['w']
        height = height if height < pdf_size[self.orientation]['h'] else pdf_size[self.orientation]['h']

        return width, height


############# TESTS #############

if __name__ == "__main__":
    PdfExporter().test()
