# Main Packages same as import uvm_pkg or uvm_defines.svh
from pyuvm import uvm_object
from s18_pyuvm_reg_block import *
from s21_pyuvm_reg_map import uvm_reg_map
from s24_pyuvm_reg_includes import *

# Class declaration
class uvm_reg(uvm_object):
    ## Constructor
    def __init__(self, name="uvm_reg", reg_width=32):
        super().__init__(name)
        self._parent    = None
        self._fields    = []
        self._err_list  = []
        self._mirrored  = 0
        self._reset     = 0
        self._name      = name
        self._header    = name + " -- "
        self._address   = "0x0"
        self._path      = ""
        self._width     = reg_width
        ## If set those 2 flags will override fields values, and if set to True the fields will report error reponse
        ## in case of (Operation,Access) expect an error
        self.throw_error_on_read    = False;
        self.throw_error_on_write   = False;       

    # configure
    def configure(self, parent: uvm_reg_block, address, hdl_path, throw_error_on_read=False, throw_error_on_write=False):
        self._parent    = parent
        self._address   = address
        self._path      = hdl_path
        ## If set those 2 flags will override fields values, and if set to True the fields will report error reponse
        ## in case of (Operation,Access) expect an error        
        self.throw_error_on_read    = throw_error_on_read;
        self.throw_error_on_write   = throw_error_on_write;
        parent._add_register(self)

    # adding error to the main error list
    def _add_error(self, value):
        self._err_list.append(value)
    
    # checking mechanims for error list
    def _check_(self):
        if(len(self._err_list) > 0):
            (print(self._err_list[el] for el in range(len(self._err_list))))

    # get parent
    def get_parent(self):
        return self._parent

    # get_fields Return fields in canonical order (LSB to MSB)
    def get_fields(self):
        return self._fields

    # _add_field
    def _add_field(self, field):
        # - field not None
        if(field == None):
            error_out(self._header, "_add_field Fields cannot be None")
            self._add_error(uvm_reg_error_decoder.FIELD_CANNOT_BE_NONE.name)
        # - field not already added
        if(field in self._fields):
            error_out(self._header, "_add_field: Fields {} is already added".format(field.name))
            self._add_error(uvm_reg_error_decoder.FIELD_ALREADY_ADDED.name)
        # - field fits in reg
        sm = 0
        for _f in self._fields:
            sm += _f.get_n_bits()
            if(self._width < sm):
                error_out(self._header, "_add_field: Fields {} doesn't fit into a {} bits register".format(field.name,self._width))      
                self._add_error(uvm_reg_error_decoder.FIELD_DOESNT_FIT_INTO_REG.name)     
        # - field doesn't overlap with any other field
        for _fi, _f in enumerate(self._fields[:-1]):
            if(_f.get_msb_pos() - self._fields[_fi+1].get_lsb_pos() > 0):
                error_out(self._header, "_add_field: Fields {} overlap with field {}".format(_f.name,self._fields[_fi+1].name))
                self._add_error(uvm_reg_error_decoder.FIELD_OVERLAPPING_ERROR.name)
        # - if we did not error out we can append the field to the list
        self._fields.append(field)

    # _set_lock
    def _set_lock(self):
        (_f.field_lock() for _f in self._fields)

    # Predict
    def predict(self, value):
        for f in self._fields:
            f.field_predict((value >> f.get_lsb_pos()),path_t.FRONTDOOR)

    # Get mirrored value
    def get_mirrored_value(self):
        for f in self._fields:
            self._mirrored = self._mirrored | (f.get_value() << f.get_lsb_pos())
        return self._mirrored

    # get_address
    def get_address(self):
        return self._address

    # Reset
    def reset(self):
        for f in self._fields:
            f.reset()
            self._mirrored = self._mirrored | (f.get_value() << f.get_lsb_pos())

    # Build internal function
    def build(self):
        ## This function needs to be implemented into the child class
        ## create each fields and invoke the configure from each field
        pass

    # Write Method (TASK)
    async def write(self, value, map: uvm_reg_map, path: path_t, check: check_t) -> pyuvm_resp_t:
        ## This Task should implement the main read method via only FRONTDOOR
        ## TODO: BACKDOOT and USER FRONTDOOR are missing
        ## This Task returns only the operation status
        ## Local Variables to be returned
        status = pyuvm_resp_t
        ## Given the map we do not check if the current register exists in the map 
        # (redundant check) since the register is directly taken from the MAP
        ## We check instead if the map is set and if only one exists (multiple access)
        if map != None:
            status = await map.process_write_operation(self.get_address(), value, path, check)
        else:
            error_out(self._header,"WRITE: map cannot be NULL")
        ## Return from Task
        return status

    # Read Method (TASK)
    async def read(self, map: uvm_reg_map, path: path_t, check: check_t):
        ## This Task should implement the main read method via only FRONTDOOR
        ## TODO: BACKDOOT and USER FRONTDOOR are missing
        ## This Task returns only the operation status and the read value 
        # (0 is status is error)
        ## Local Variables to be returned
        status = pyuvm_resp_t
        ## Given the map we do not check if the current register exists in the map 
        # (redundant check) since the register is directly taken from the MAP
        ## We check instead if the map is set and if only one exists (multiple access)
        if map != None:
            status, read_data = await map.process_read_operation(self.get_address(), path, check)
            if status == pyuvm_resp_t.ERROR_RESP:
                read_data = 0
        else:
            error_out(self._header,"READ: map cannot be NULL")
        ## Return from Task
        return status, read_data
