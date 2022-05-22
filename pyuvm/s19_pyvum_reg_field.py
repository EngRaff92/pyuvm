# Main Packages same as import uvm_pkg or uvm_defines.
from pyuvm import uvm_object
from s24_pyuvm_reg_includes import *

# Class declaration for register field
#@rand_enable(enable_pyvsc)
class uvm_reg_field(uvm_object):

    ## constructor
    def __init__(self, name='uvm_reg_field'):
        super().__init__(name)
        self.access_list    = ["RO","RW","RC","RS","WC","WS","W1C","W1S","W1T","W0C","W0S","W0T","WRC","WRS","W1SRC","W1CRS","W0SRC","W0CRS","WSRC","WCRS","WO","WOC","WOS","W1","WO1"]
        self._parent        = None
        self._size          = 0
        self._lsb_pos       = None
        self._access        = "" # Start with empty access
        self._is_volatile   = None
        self._reset         = 0
        self._field_mirrored= 0
        self._value         = 0
        ## Keep desired value as random 
        if enable_pyvsc == True:
            self._desidered     = vsc.rand_bit_t(self._size)
        else:
            self._desidered     = 0
        self._config_done   = False
        self._has_been_writ = False
        self._prediction    = predict_t
        self._response      = pyuvm_resp_t
        self._name          = name
        self._header        = name + " -- "    
        ## These 2 flags cannot change for fields since are part of the parent register
        self._error_on_read = False
        self._error_on_write= False

    ## configure
    def configure(self, parent, size, lsb_pos, access, is_volatile, reset):
        self._parent        = parent
        parent._add_field(self)
        self._size          = size
        self._lsb_pos       = lsb_pos
        self._access        = access
        self._is_volatile   = is_volatile
        self._reset         = reset
        self._config_done   = False
        self._compare       = check_t
        ## Additional Checking
        ## Ignore randomization if the field is known not to be writeable
        ## i.e. not "RW", "WRC", "WRS", "WO", "W1", "WO1"
        if enable_pyvsc == True:
            if self._access in ["RW", "WRC", "WRS", "WO", "W1", "WO1"]:
                self._desidered.rand_mode = True
            else:
                self._desidered.rand_mode = False
        else:
            self._desidered = 0
        ## These 2 flags cannot change for fields since are part of the parent register
        self._error_on_read = parent.throw_error_on_read
        self._error_on_write= parent.throw_error_on_write            

    ## lock method meaning the configursation is done and we can unlock all the internal methods
    def field_lock(self):
        self._config_done = True

    ## set_compare
    def set_compare(self, check_type: check_t):
        self._check = check_type

    ## set_throw_error_on_read
    def set_throw_error_on_read(self, teor=False):
        self._error_on_read = teor

    ## set_throw_error_on_write
    def set_throw_error_on_write(self, teow=False):
        self._error_on_write = teow

    ## get_compare
    def get_compare(self):
        return self._check;

    ## get_full_name
    def get_full_name(self):
        return self._parent+"."+self._name

    ## get_name
    def get_name(self):
        return self._name

    ## get_parent
    def get_parent(self):
        if self._config_done == False:
            error_out(self._header,"Configure for a field must be called called before any other memeber method")
        else:
            return self._parent

    ## get_lsb_pos
    def get_lsb_pos(self) -> int:
        if self._config_done == False:
            error_out(self._header,"Configure for a field must be called called before any other memeber method")
            return 0
        else:
            return self._lsb_pos

    ## get_msb_pos
    def get_msb_pos(self) -> int:
        if self._config_done == False:
            error_out(self._header,"Configure for a field must be called called before any other memeber method")
            return 0
        else:
            return self._lsb_pos + self._size - 1     

    ## get_n_bits
    def get_n_bits(self) -> int:
        if self._config_done == False:
            error_out(self._header,"Configure for a field must be called called before any other memeber method")
            return 0
        else:
            return self._size

    ## get_access 
    def get_access(self) -> str:
        if self._config_done == False:
            error_out(self._header,"Configure for a field must be called called before any other memeber method")
        else:
            return self._access

    ## is_volatile
    def is_volatile(self):
        if self._config_done == False:
            error_out(self._header,"Configure for a field must be called called before any other memeber method")
        else:
            return self._is_volatile

    # get_reset
    def get_reset(self) -> int:
        if self._config_done == False:
            error_out(self._header,"Configure for a field must be called called before any other memeber method")
        else:
            return self._reset
    
    # atomic get value
    def get(self):
        return self._desidered

    # atomic reset value
    def reset(self):
        self._field_mirrored    = self._reset
        self._has_been_writ     = False
        self._response          = pyuvm_resp_t.PASS_RESP

    # atomic get value
    def get_value(self):
        return self._field_mirrored

    # Atomic set access value
    def set_access(self,access_value):
        if (not isinstance(access_value,str)):
            error_out(self._header,"Access set for reg field needs to be a string")
        else:
            if (access_value is self.access_list):
                self._access = access_value
            else:
                error_out(self._header,"Access value provided is not part of possible access values")
                self._access = "NOACCESS"

    # Atomic set response status for fields
    def set_response(self, f_response: pyuvm_resp_t):
        self._response = f_response

    # Atomic set prediction type for field. This comes from the register parent
    def set_prediction(self, pred_type: predict_t):
        self._prediction = pred_type

    # Atomic get status from fields
    def get_response(self):
        return self._response

    # atomic set value
    def field_set(self,value):
        ## Define an all 1 values
        _mask = int("".join(["1"]*self._size),2)
        ## Return value based on the access
        if self.get_access() == "RO":    
            pass ## Leave the desired value stable
        if self.get_access() == "RW":    
            self._desidered = value
        if self.get_access() == "RC":    
            pass ## Leave the desired value stable
        if self.get_access() == "RS":    
            pass ## Leave the desired value stable
        if self.get_access() == "WC":    
            self._desidered = 0
        if self.get_access() == "WS":    
            self._desidered = _mask
        if self.get_access() == "WRC":   
            self._desidered = value
        if self.get_access() == "WRS":   
            self._desidered = value
        if self.get_access() == "WSRC":  
            self._desidered = _mask
        if self.get_access() == "WCRS":  
            self._desidered = 0
        if self.get_access() == "W1C":   
            self._desidered = self._desidered & (~value)
        if self.get_access() == "W1S":   
            self._desidered = self._desidered | value
        if self.get_access() == "W1T":   
            self._desidered = self._desidered ^ value
        if self.get_access() == "W0C":   
            self._desidered = self._desidered & value
        if self.get_access() == "W0S":   
            self._desidered = self._desidered | (~value & _mask)
        if self.get_access() == "W0T":   
            self._desidered = self._desidered ^ (~value & _mask)
        if self.get_access() == "W1SRC": 
            self._desidered = self._desidered | value
        if self.get_access() == "W1CRS": 
            self._desidered = self._desidered & (~value)
        if self.get_access() == "W0SRC": 
            self._desidered = self._desidered | (~value & _mask)
        if self.get_access() == "W0CRS": 
            self._desidered = self._desidered & value
        if self.get_access() == "WO":    
            self._desidered = value
        if self.get_access() == "WOC":   
            self._desidered = 0
        if self.get_access() == "WOS":  
            self._desidered = _mask
        if self.get_access() == "W1":   
            if self._has_been_writ == True:
                pass ## Leave the desired value stable
            else:
                self._desidered = value
        if self.get_access() == "WO1":   
            if self._has_been_writ == True:
                pass ## Leave the desired value stable
            else:
                self._desidered = value
        if self.get_access() == "NOACCESS": 
            pass ## Leave the desired value stable

    ## Since there is no Switch case in python we use a simple switch case
    # Where error is mentioned it depends on _error_on_write flag, no effect will be translated in Error reponse if flag is enable
    ## "RO"       - W: no effect, R: no effect
    ## "RW"       - W: as-is, R: no effect
    ## "RC"       - W: no effect, R: clears all bits
    ## "RS"       - W: no effect, R: sets all bits
    ## "WRC"      - W: as-is, R: clears all bits
    ## "WRS"      - W: as-is, R: sets all bits
    ## "WC"       - W: clears all bits, R: no effect
    ## "WS"       - W: sets all bits, R: no effect
    ## "WSRC"     - W: sets all bits, R: clears all bits
    ## "WCRS"     - W: clears all bits, R: sets all bits
    ## "W1C"      - W: 1/0 clears/no effect on matching bit, R: no effect
    ## "W1S"      - W: 1/0 sets/no effect on matching bit, R: no effect
    ## "W1T"      - W: 1/0 toggles/no effect on matching bit, R: no effect
    ## "W0C"      - W: 1/0 no effect on/clears matching bit, R: no effect
    ## "W0S"      - W: 1/0 no effect on/sets matching bit, R: no effect
    ## "W0T"      - W: 1/0 no effect on/toggles matching bit, R: no effect
    ## "W1SRC"    - W: 1/0 sets/no effect on matching bit, R: clears all bits
    ## "W1CRS"    - W: 1/0 clears/no effect on matching bit, R: sets all bits
    ## "W0SRC"    - W: 1/0 no effect on/sets matching bit, R: clears all bits
    ## "W0CRS"    - W: 1/0 no effect on/clears matching bit, R: sets all bits
    ## "WO"       - W: as-is, R: error
    ## "WOC"      - W: clears all bits, R: error
    ## "WOS"      - W: sets all bits, R: error
    ## "W1"       - W: first one after ~HARD~ reset is as-is, other W have no effects, R: no effect
    ## "WO1"      - W: first one after ~HARD~ reset is as-is, other W have no effects, R: error
    ## "NOACCESS" - W: no effect, R: no effect    
    def predict_based_on_write(self, wr_val):
        ## Define an all 1 values
        _mask = int("".join(["1"]*self._size),2)
        ## Return value based on the access type
        if self.get_access() == "RO":    
            self._field_mirrored = self._reset
        if self.get_access() == "RW":    
            self._field_mirrored = wr_val
        if self.get_access() == "RC":    
            self._field_mirrored = self._field_mirrored
        if self.get_access() == "RS":    
            self._field_mirrored = self._field_mirrored
        if self.get_access() == "WC":    
            self._field_mirrored = 0
        if self.get_access() == "WS":    
            self._field_mirrored = _mask
        if self.get_access() == "WRC":   
            self._field_mirrored = wr_val
        if self.get_access() == "WRS":   
            self._field_mirrored = wr_val
        if self.get_access() == "WSRC":  
            self._field_mirrored = _mask
        if self.get_access() == "WCRS":  
            self._field_mirrored = 0
        if self.get_access() == "W1C":   
            self._field_mirrored = self._field_mirrored & (~wr_val)
        if self.get_access() == "W1S":   
            self._field_mirrored = self._field_mirrored | wr_val
        if self.get_access() == "W1T":   
            self._field_mirrored = self._field_mirrored ^ wr_val
        if self.get_access() == "W0C":   
            self._field_mirrored = self._field_mirrored & wr_val
        if self.get_access() == "W0S":   
            self._field_mirrored = self._field_mirrored | (~wr_val & _mask)
        if self.get_access() == "W0T":   
            self._field_mirrored = self._field_mirrored ^ (~wr_val & _mask)
        if self.get_access() == "W1SRC": 
            self._field_mirrored = self._field_mirrored | wr_val
        if self.get_access() == "W1CRS": 
            self._field_mirrored = self._field_mirrored & (~wr_val)
        if self.get_access() == "W0SRC": 
            self._field_mirrored = self._field_mirrored | (~wr_val & _mask)
        if self.get_access() == "W0CRS": 
            self._field_mirrored = self._field_mirrored & wr_val
        if self.get_access() == "WO":    
            self._field_mirrored = wr_val
        if self.get_access() == "WOC":   
            self._field_mirrored = 0
        if self.get_access() == "WOS":  
            self._field_mirrored = _mask
        if self.get_access() == "W1":   
            if self._has_been_writ == True:
                self._field_mirrored = self._field_mirrored 
            else:
                self._field_mirrored = wr_val
        if self.get_access() == "WO1":   
            if self._has_been_writ == True:
                self._field_mirrored = self._field_mirrored 
            else:
                self._field_mirrored = wr_val
        if self.get_access() == "NOACCESS": 
            self._field_mirrored = self._reset

    # atomic predict value based on the operation (READ)
    # Where error is mentioned it depends on _error_on_read flag, no effect will be translated in Error reponse if flag is enable
    ## Since there is no Switch case in python we use a simple switch case
    ## "RO"       - W: no effect, R: return the mirrored value (reset one)
    ## "RW"       - W: as-is, R: as-is
    ## "RC"       - W: no effect, R: clears all bits
    ## "RS"       - W: no effect, R: sets all bits
    ## "WRC"      - W: as-is, R: clears all bits
    ## "WRS"      - W: as-is, R: sets all bits
    ## "WC"       - W: clears all bits, R: no effect
    ## "WS"       - W: sets all bits, R: no effect
    ## "WSRC"     - W: sets all bits, R: clears all bits
    ## "WCRS"     - W: clears all bits, R: sets all bits
    ## "W1C"      - W: 1/0 clears/no effect on matching bit, R: no effect
    ## "W1S"      - W: 1/0 sets/no effect on matching bit, R: no effect
    ## "W1T"      - W: 1/0 toggles/no effect on matching bit, R: no effect
    ## "W0C"      - W: 1/0 no effect on/clears matching bit, R: no effect
    ## "W0S"      - W: 1/0 no effect on/sets matching bit, R: no effect
    ## "W0T"      - W: 1/0 no effect on/toggles matching bit, R: no effect
    ## "W1SRC"    - W: 1/0 sets/no effect on matching bit, R: clears all bits
    ## "W1CRS"    - W: 1/0 clears/no effect on matching bit, R: sets all bits
    ## "W0SRC"    - W: 1/0 no effect on/sets matching bit, R: clears all bits
    ## "W0CRS"    - W: 1/0 no effect on/clears matching bit, R: sets all bits
    ## "WO"       - W: as-is, R: error
    ## "WOC"      - W: clears all bits, R: error
    ## "WOS"      - W: sets all bits, R: error
    ## "W1"       - W: first one after ~HARD~ reset is as-is, other W have no effects, R: no effect
    ## "WO1"      - W: first one after ~HARD~ reset is as-is, other W have no effects, R: error
    ## "NOACCESS" - W: no effect, R: no effect    
    def predict_based_on_read(self,value):
        ## FRONTDOOR
        if self.get_access() in ["RC","WRC","WSRC","W1SRC","W0SRC"]:
            ## Set Value to 0 since READ will clear
            self._field_mirrored = 0; 
        elif self.get_access() in ["RS","WRS","WCRS","W1CRS","W0CRS"]:
            ## Set Value to 1 since READ will set to 1
            self._field_mirrored = int("".join(["1"]*self._size),2) 
        elif self.get_access() in ["WO","WOC","WOS","WO1","NOACCESS","W1","W1T","W0T","WC","WS","W1C","W1S","W0C","W0S"]:
            ## Set Value to the reset since READ will have no effect
            self._field_mirrored = self._reset
        else:
            error_out(self._header,"Wrong Access set on predict_based_on_read")

    # Check the Direction and the access type along with the enable error flags (if error is supposed to be thown then send it out)
    def predict_response(self, value, path: path_t, direction: access_e):
        ## Check the Direction and the access type along with the enable error flags (if error is supposed to be thown then send it out)
        ## if we try to write a 1 when the access on write will require the 0 to generate some effect
        if((direction == access_e.PYUVM_WRITE) & (self.get_access() in ["RO","RW","RC","RS"]) & (path == path_t.FRONTDOOR)):
            self.set_response(pyuvm_resp_t.PASS_RESP if(self._error_on_write == False) else pyuvm_resp_t.ERROR_RESP)
        elif((direction == access_e.PYUVM_READ) & (self.get_access() in ["WO","WOC","WOS","WO1","NOACCESS","W1","W1T","W0T","WC","WS","W1C","W1S","W0C","W0S"]) & (path == path_t.FRONTDOOR)):
            self.set_response(pyuvm_resp_t.PASS_RESP if(self._error_on_read == False) else pyuvm_resp_t.ERROR_RESP) 
        else: ## This will include the BACKDOOR
            self.set_response(pyuvm_resp_t.PASS_RESP)

    # Main field prediction function to be used to predict mirrored value for pyuvm_fields
    def field_predict(self, value, path: path_t, direction: access_e):      
        ## Predict the status based on the flags
        self.predict_response(value, path, direction)
        ## WRITE prediction and prediction is ether on write and Direct
        if((direction == access_e.PYUVM_WRITE) & (path == path_t.FRONTDOOR) & (self._prediction in [predict_t.PREDICT_DIRECT, predict_t.PREDICT_WRITE])):
            self.predict_based_on_write(value)
        ## READ prediction and prediction is ether on read and Direct
        elif((direction == access_e.PYUVM_READ) & (path == path_t.FRONTDOOR) & (self._prediction in [predict_t.PREDICT_DIRECT, predict_t.PREDICT_READ])):
            self.predict_based_on_read(value)
        elif(path == path_t.BACKDOOR):
            self._field_mirrored = value
            self.set_response(pyuvm_resp_t.PASS_RESP)
        else:
            error_out(self._header,"Wrong combination of PATH - PREDICTION TYPE and DIRECTION on pyuvm_field -- field_predict function")

        