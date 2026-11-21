IF ((f1 > ( (HH - x1sensor) /e))) THEN	V1:= 0; ELSE	
IF (( NOT(f1 > ( (HH - x1sensor) /e)))) THEN	
IF ((x1sensor < L1)) THEN	V1:= 1; 
END_IF;
END_IF;
END_IF; 
IF ((x2 < L2)) THEN	P:= 1;  V2:= 1; 
END_IF; 
IF (((((V1 * f1) - ((V2 * P) * f2)) < ( (LL - x1sensor) /e)) OR ((f2 < FL) OR (((V2 * P) * f2) > ( (HH - x2) /e))))) THEN	P:= 0;  V2:= 0; 
END_IF; t:= 0;  
