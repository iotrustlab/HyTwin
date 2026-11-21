PROGRAM plc2
  VAR
    ColorSensor_RED AT %QW0 : INT;
    ColorSensor_GREEN AT %QW1 : INT;
    ColorSensor_BLUE AT %QW2 : INT;
    RangeSensor AT %QW3 : INT;
    Pump AT %QX0.4 : BOOL := FALSE;
    Doser_RED AT %QX0.6 : BOOL := FALSE;
    Doser_BLUE AT %QX0.7 : BOOL := FALSE;
  END_VAR
  VAR
    settleTime : TIME := T#700ms;
    doseTime : TIME := T#2000ms;
  END_VAR
  VAR
    treatmentComplete AT %QX0.0 : BOOL := FALSE;
    stage AT %QW4 : INT := 0;
  END_VAR
  VAR
    desiredDistanceFill : REAL := 7.0;
  END_VAR
  VAR
    measuredDistance AT %QD1 : REAL;
  END_VAR
  VAR
    minRed : INT := 20;
    doserRedTimer : TON;
    doserBlueTimer : TON;
    settleTimer : TON;
  END_VAR
  VAR
    doseTimerDone AT %QX1.2 : BOOL := 0;
  END_VAR
  VAR
    settleEN : BOOL := FALSE;
  END_VAR


  (*Workaround to distance measure bug*)
  measuredDistance :=  INT_TO_REAL(RangeSensor)/100.0;
  desiredDistanceFill := 7.0;
  minRed := 20;
  doseTime := T#3000ms;
  settleTime := T#5000ms;

  doserRedTimer(IN:=Doser_RED, PT:=doseTime);
  doserBlueTimer(IN:=Doser_BLUE,PT:=doseTime);
  doseTimerDone := doserRedTimer.Q;
  settleTimer(IN:=settleEN, PT:=settleTime);

  CASE stage OF
      0:  (*Filling stage: it will fill up to a certain amount that corresponds to a certain distance*)
      
          IF measuredDistance > desiredDistanceFill THEN
            Pump := TRUE;
          ELSE
            Pump := FALSE;
            stage := 1;
          END_IF;
          
     1:  (*Treatment stage*)
      
          IF ColorSensor_RED < minRed THEN (*Ensure minimum red value is inserted*)
            stage := 2;
            Doser_RED := TRUE;
            
          ELSIF ColorSensor_RED > ColorSensor_BLUE  THEN (*Ensure blue quantity is > Red *)
            
              stage := 3;
              Doser_BLUE := TRUE;
          
          ELSE  (*Treatment complete*)
            
            stage := 5;
            
          END_IF;
          
      2:  (*Red Dosing Stage*)
      
          IF doserRedTimer.Q THEN
            Doser_RED := FALSE;
            stage := 4;
            settleEN := True;
            (*settleTimer(IN:= True, PT:= settleTime); (*let the dose settle*)
          END_IF;
          
      3: (* Blue Dosing Stage*)
      
          IF doserBlueTimer.Q THEN
            Doser_BLUE := FALSE;
            stage := 4;
            settleEN := True;
          END_IF;
          
      4: (*Settling Stage for Dosage*)
      
          IF settleTimer.Q THEN
            stage := 1;
            settleEN := False;
          END_IF;
      
      5: (*Treatment Complete*)
      
        treatmentComplete := TRUE;
        
  END_CASE;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : plc2;
  END_RESOURCE
END_CONFIGURATION

(*DBG:char md5[] = "85c0d8f829b91cde4675ebd7ca2ce9aa";*)
(*DBG:/**)
(*DBG: * This file is part of OpenPLC Runtime*)
(*DBG: **)
(*DBG: * Copyright (C) 2023 Autonomy, GP Orcullo*)
(*DBG: * Based on the work by GP Orcullo on Beremiz for uC*)
(*DBG: **)
(*DBG: * This program is free software; you can redistribute it and/or*)
(*DBG: * modify it under the terms of the GNU General Public License*)
(*DBG: * as published by the Free Software Foundation; either version 2*)
(*DBG: * of the License, or (at your option) any later version.*)
(*DBG: **)
(*DBG: * This program is distributed in the hope that it will be useful,*)
(*DBG: * but WITHOUT ANY WARRANTY; without even the implied warranty of*)
(*DBG: * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the*)
(*DBG: * GNU General Public License for more details.*)
(*DBG: **)
(*DBG: * You should have received a copy of the GNU General Public License*)
(*DBG: * along with this program; If not, see <http://www.gnu.org/licenses/>.*)
(*DBG: **)
(*DBG: */*)
(*DBG:*)
(*DBG:#include <stdbool.h>*)
(*DBG:*)
(*DBG:#include "iec_types_all.h"*)
(*DBG:#include "POUS.h"*)
(*DBG:*)
(*DBG:#define SAME_ENDIANNESS      0*)
(*DBG:#define REVERSE_ENDIANNESS   1*)
(*DBG:*)
(*DBG:uint8_t endianness;*)
(*DBG:*)
(*DBG:*)
(*DBG:extern PLC2 RES0__INSTANCE0;*)
(*DBG:*)
(*DBG:static const struct {*)
(*DBG:    void *ptr;*)
(*DBG:    __IEC_types_enum type;*)
(*DBG:} debug_vars[] = {*)
(*DBG:    {&(RES0__INSTANCE0.COLORSENSOR_RED), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COLORSENSOR_GREEN), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.COLORSENSOR_BLUE), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.RANGESENSOR), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PUMP), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSER_RED), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSER_BLUE), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSETIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.TREATMENTCOMPLETE), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.STAGE), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DESIREDDISTANCEFILL), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.MEASUREDDISTANCE), REAL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.MINRED), INT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERREDTIMER.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERREDTIMER.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERREDTIMER.IN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERREDTIMER.PT), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERREDTIMER.Q), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERREDTIMER.ET), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERREDTIMER.STATE), SINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERREDTIMER.PREV_IN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERREDTIMER.CURRENT_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERREDTIMER.START_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERBLUETIMER.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERBLUETIMER.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERBLUETIMER.IN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERBLUETIMER.PT), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERBLUETIMER.Q), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERBLUETIMER.ET), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERBLUETIMER.STATE), SINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERBLUETIMER.PREV_IN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERBLUETIMER.CURRENT_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSERBLUETIMER.START_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIMER.EN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIMER.ENO), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIMER.IN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIMER.PT), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIMER.Q), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIMER.ET), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIMER.STATE), SINT_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIMER.PREV_IN), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIMER.CURRENT_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLETIMER.START_TIME), TIME_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DOSETIMERDONE), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.SETTLEEN), BOOL_ENUM},*)
(*DBG:};*)
(*DBG:*)
(*DBG:#define VAR_COUNT               46*)
(*DBG:*)
(*DBG:uint16_t get_var_count(void)*)
(*DBG:{*)
(*DBG:    return VAR_COUNT;*)
(*DBG:}*)
(*DBG:*)
(*DBG:size_t get_var_size(size_t idx)*)
(*DBG:{*)
(*DBG:    if (idx >= VAR_COUNT)*)
(*DBG:    {*)
(*DBG:        return 0;*)
(*DBG:    }*)
(*DBG:    switch (debug_vars[idx].type) {*)
(*DBG:    case TIME_ENUM:*)
(*DBG:        return sizeof(TIME);*)
(*DBG:    case REAL_ENUM:*)
(*DBG:        return sizeof(REAL);*)
(*DBG:    case BOOL_ENUM:*)
(*DBG:        return sizeof(BOOL);*)
(*DBG:    case SINT_ENUM:*)
(*DBG:        return sizeof(SINT);*)
(*DBG:    case INT_ENUM:*)
(*DBG:        return sizeof(INT);*)
(*DBG:    default:*)
(*DBG:        return 0;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void *get_var_addr(size_t idx)*)
(*DBG:{*)
(*DBG:    void *ptr = debug_vars[idx].ptr;*)
(*DBG:*)
(*DBG:    switch (debug_vars[idx].type) {*)
(*DBG:    case TIME_ENUM:*)
(*DBG:        return (void *)&((__IEC_TIME_t *) ptr)->value;*)
(*DBG:    case REAL_ENUM:*)
(*DBG:        return (void *)&((__IEC_REAL_t *) ptr)->value;*)
(*DBG:    case BOOL_ENUM:*)
(*DBG:        return (void *)&((__IEC_BOOL_t *) ptr)->value;*)
(*DBG:    case SINT_ENUM:*)
(*DBG:        return (void *)&((__IEC_SINT_t *) ptr)->value;*)
(*DBG:    case INT_ENUM:*)
(*DBG:        return (void *)&((__IEC_INT_t *) ptr)->value;*)
(*DBG:    default:*)
(*DBG:        return 0;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void force_var(size_t idx, bool forced, void *val)*)
(*DBG:{*)
(*DBG:    void *ptr = debug_vars[idx].ptr;*)
(*DBG:*)
(*DBG:    if (forced) {*)
(*DBG:        size_t var_size = get_var_size(idx);*)
(*DBG:        switch (debug_vars[idx].type) {*)
(*DBG:        case TIME_ENUM: {*)
(*DBG:            memcpy(&((__IEC_TIME_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_TIME_t *) ptr)->value = *((TIME *) val);*)
(*DBG:            ((__IEC_TIME_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        case REAL_ENUM: {*)
(*DBG:            memcpy(&((__IEC_REAL_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_REAL_t *) ptr)->value = *((REAL *) val);*)
(*DBG:            ((__IEC_REAL_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        case BOOL_ENUM: {*)
(*DBG:            memcpy(&((__IEC_BOOL_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_BOOL_t *) ptr)->value = *((BOOL *) val);*)
(*DBG:            ((__IEC_BOOL_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        case SINT_ENUM: {*)
(*DBG:            memcpy(&((__IEC_SINT_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_SINT_t *) ptr)->value = *((SINT *) val);*)
(*DBG:            ((__IEC_SINT_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        case INT_ENUM: {*)
(*DBG:            memcpy(&((__IEC_INT_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_INT_t *) ptr)->value = *((INT *) val);*)
(*DBG:            ((__IEC_INT_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        default:*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:    } else {*)
(*DBG:        switch (debug_vars[idx].type) {*)
(*DBG:        case TIME_ENUM:*)
(*DBG:            ((__IEC_TIME_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        case REAL_ENUM:*)
(*DBG:            ((__IEC_REAL_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        case BOOL_ENUM:*)
(*DBG:            ((__IEC_BOOL_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        case SINT_ENUM:*)
(*DBG:            ((__IEC_SINT_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        case INT_ENUM:*)
(*DBG:            ((__IEC_INT_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        default:*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void swap_bytes(void *ptr, size_t size) *)
(*DBG:{*)
(*DBG:    uint8_t *bytePtr = (uint8_t *)ptr;*)
(*DBG:    size_t i;*)
(*DBG:    for (i = 0; i < size / 2; ++i) *)
(*DBG:    {*)
(*DBG:        uint8_t temp = bytePtr[i];*)
(*DBG:        bytePtr[i] = bytePtr[size - 1 - i];*)
(*DBG:        bytePtr[size - 1 - i] = temp;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void trace_reset(void)*)
(*DBG:{*)
(*DBG:    for (size_t i=0; i < VAR_COUNT; i++) *)
(*DBG:    {*)
(*DBG:        force_var(i, false, 0);*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void set_trace(size_t idx, bool forced, void *val)*)
(*DBG:{*)
(*DBG:    if (idx >= 0 && idx < VAR_COUNT) *)
(*DBG:    {*)
(*DBG:        if (endianness == REVERSE_ENDIANNESS)*)
(*DBG:        {*)
(*DBG:            // Aaaaarghhhh... Stupid AVR is Big Endian.*)
(*DBG:            swap_bytes(val, get_var_size(idx));*)
(*DBG:        }*)
(*DBG:*)
(*DBG:        force_var(idx, forced, val);*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void set_endianness(uint8_t value)*)
(*DBG:{*)
(*DBG:    if (value == SAME_ENDIANNESS || value == REVERSE_ENDIANNESS)*)
(*DBG:    {*)
(*DBG:        endianness = value;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)