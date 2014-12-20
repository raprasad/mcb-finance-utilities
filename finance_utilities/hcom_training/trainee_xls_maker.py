import xlwt
from xlwt import easyxf
from finance_utilities.common.xls_styles import *

# Text values for colour indices. "grey" is a synonym of "gray".
# The names are those given by Microsoft Excel 2003 to the colours
# in the default palette. There is no great correspondence with
# any W3C name-to-RGB mapping.
_colour_map_text = """aqua 0x31
black 0x08
blue 0x0C
blue_gray 0x36
bright_green 0x0B
brown 0x3C
coral 0x1D
cyan_ega 0x0F
dark_blue 0x12
dark_blue_ega 0x12
dark_green 0x3A
dark_green_ega 0x11
dark_purple 0x1C
dark_red 0x10
dark_red_ega 0x10
dark_teal 0x38
dark_yellow 0x13
gold 0x33
gray_ega 0x17
gray25 0x16
gray40 0x37
gray50 0x17
gray80 0x3F
green 0x11
ice_blue 0x1F
indigo 0x3E
ivory 0x1A
lavender 0x2E
light_blue 0x30
light_green 0x2A
light_orange 0x34
light_turquoise 0x29
light_yellow 0x2B
lime 0x32
magenta_ega 0x0E
ocean_blue 0x1E
olive_ega 0x13
olive_green 0x3B
orange 0x35
pale_blue 0x2C
periwinkle 0x18
pink 0x0E
plum 0x3D
purple_ega 0x14
red 0x0A
rose 0x2D
sea_green 0x39
silver_ega 0x16
sky_blue 0x28
tan 0x2F
teal 0x15
teal_ega 0x15
turquoise 0x0F
violet 0x14
white 0x09
yellow 0x0D""".split('\n')


def make_trainee_roster(sheet1, info_line, trainees):
    if sheet1 is None:
        return None
    if trainees is None:
        return sheet
    
    row_num =0
    if info_line:
        sheet1.write(row_num, 2, info_line, style_info_cell)
    
    row_num+=1
    sheet1.write(row_num, 2, 'MCB HCOM Training Attendance List', style_info_cell_bold)
    
    # header column
    row_num+=1
    col_names = """(Special), Last Name, First Name, Email, Active, Confirmed Training, Completed Training, Hands On Training Date, Demo Training Date, Approver or Shopper, Lab/Office, Training Order, Training Location, Notes""".split(',')
    col_names = map(lambda x: x.strip(), col_names)
    for idx, col_name in enumerate(col_names):
        sheet1.write(row_num, idx, col_name, style_header_gray)

    """
    # color test
    for idx2, item in enumerate(_colour_map_text):
        cname, ccode = item.split()
        style_info_cell_col = easyxf('pattern: pattern solid, fore_colour %s;align: wrap off;align:vert top; borders: top thin, bottom thin, right thin, left thin;' % cname)
        sheet1.write(0, idx2+5, cname, style_info_cell_col)
    """
    
    char_multiplier = 256

    # Set the column widths for the spreadsheet, based on the widest value for each column
    #    
    if trainees.count() > 0:
        sheet1.col(0).width =  20  * char_multiplier    # "special"     max([attr_len(trainee.special) for trainee in trainees]) * char_multiplier+ char_multiplier
        sheet1.col(1).width = max([attr_len(trainee.lname) for trainee in trainees]) * char_multiplier+ char_multiplier
        sheet1.col(2).width = max([attr_len(trainee.fname) for trainee in trainees]) * char_multiplier + char_multiplier
        sheet1.col(3).width = max([attr_len(trainee.email) for trainee in trainees]) * char_multiplier + char_multiplier
        sheet1.col(4).width = 20  * char_multiplier     # active
        sheet1.col(5).width = 20  * char_multiplier     # confirmed training
        sheet1.col(6).width = 20  * char_multiplier     # completed training
        sheet1.col(7).width = 35  * char_multiplier     # hands-on date
        sheet1.col(8).width = 35  * char_multiplier     # demo date
        sheet1.col(9).width = 20  * char_multiplier     # approver/shopper
        sheet1.col(10).width = max([attr_len(trainee.lab_or_office.name) for trainee in trainees]) * char_multiplier + char_multiplier
        sheet1.col(11).width = 20  * char_multiplier     # train ing order
        
        sheet1.col(12).width = 40 *  char_multiplier    # trianing room max([attr_len(str(trainee.location.room)) for trainee in trainees]) * char_multiplier + char_multiplier
        
        sheet1.col(13).width =  35  * char_multiplier     # notes
     

    #   Add data to the spreadsheet
    #
    for trainee in trainees:
        
        #row_xls_style = style_info_cell
        try:
            if trainee.special and trainee.special.name.lower() == 'hands-on': 
                row_xls_style = style_info_cell_light_blue
                wrap_on_style = style_info_cell_light_blue_wrap_on
            elif trainee.special and trainee.special.name.lower() == 'faculty': 
                row_xls_style = style_info_cell_light_yellow
                wrap_on_style = style_info_cell_light_yellow_wrap_on
            else:
                row_xls_style = style_info_cell
                wrap_on_style = style_info_cell_wrap_on
        except:
            row_xls_style = style_info_cell
            wrap_on_style = style_info_cell_wrap_on
            
        row_num +=1
        try:
            sheet1.write(row_num, 0, trainee.special.name, row_xls_style)   # fname 
        except:
            sheet1.write(row_num, 0, 'blank', row_xls_style)   # fname 
            
        sheet1.write(row_num, 1, trainee.lname, row_xls_style)   # lname 
        sheet1.write(row_num, 2, trainee.fname, row_xls_style)   # fname 
        sheet1.write(row_num, 3, trainee.email, row_xls_style)  # email 
        if trainee.active:
            sheet1.write(row_num, 4, 'YES', row_xls_style)  
        else:
            sheet1.write(row_num, 4, 'no', row_xls_style)  
            

        if trainee.confirmed_training_date:
            sheet1.write(row_num, 5, 'YES', row_xls_style)  
        else:
            sheet1.write(row_num, 5, 'no', row_xls_style)  
            
        if trainee.completed_training:
            sheet1.write(row_num, 6, 'YES', row_xls_style)  
        else:
            sheet1.write(row_num, 6, 'no', row_xls_style)  
            
        if trainee.hands_on_training_date:
            sheet1.write(row_num, 7, trainee.hands_on_training_date.strftime('%m/%d/%Y'), row_xls_style)  
        else:
            sheet1.write(row_num, 7, '', row_xls_style)  

        if trainee.demo_training_date:
            sheet1.write(row_num, 8, trainee.demo_training_date.strftime('%m/%d/%Y'), row_xls_style)  
        else:
            sheet1.write(row_num, 8, '', row_xls_style)  

            
        sheet1.write(row_num, 9, trainee.approver_or_shopper, row_xls_style)  
        sheet1.write(row_num, 10, trainee.lab_or_office.name, row_xls_style)  
        sheet1.write(row_num, 11, trainee.training_order, row_xls_style)  
        if trainee.location and trainee.location.room:
            sheet1.write(row_num, 12, trainee.location.room, row_xls_style)  
        else:
            sheet1.write(row_num, 12, '(blank)', row_xls_style)  
            
        sheet1.write(row_num, 13, trainee.notes, wrap_on_style)  
        
    return sheet1
    
