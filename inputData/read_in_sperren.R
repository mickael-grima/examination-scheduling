
read_raum_sperren = function(filename, begin) {
    
    # Read Raumsperren
    raumsp = read.csv(filename, header=TRUE, sep=';')

    #ID_RAUM;ZUSATZBEZEICHNUNG;WOCHENTAG;TAG;ZEIT_VON;ZEIT_BIS;BIS_TAG;BIS_ZEIT

    # match times to our time slots
    N2 = length(raumsp$ID_RAUM)

    get_time2 = function (tag, zeit) {
        return(strptime(paste(tag, zeit), format = "%d/%m/%Y %H:%M"))
    }

    raum_id = raumsp$ID_RAUM
    raumsp[, "startTime"] = rep(0, N2)
    raumsp[, "endTime"] = rep(0, N2)
    
    for(i in seq(1, N2, 1)) {

        begin_tag = raumsp$TAG[i]
        end_tag = begin_tag
        
        begin_zeit = raumsp$ZEIT_VON[i]
        end_zeit = raumsp$ZEIT_BIS[i]
        
        if(begin_zeit == "0:00") {
            begin_zeit = "0:01"
        }
        
        if( length(grep(pattern=".*-.*", x=raumsp$BIS_TAG[i] , value=TRUE)) == 0 ) { 
            end_tag = raumsp$BIS_TAG[i] 
            end_zeit = raumsp$BIS_ZEIT[i] 
            
        }
        
        start = get_time2(begin_tag, begin_zeit)
        ende = get_time2(end_tag, end_zeit)
        
        raumsp[i, "startDate"] = paste(start)
        raumsp[i, "endDate"] = paste(ende)
        
        raumsp[i, "startTime"] = abs(difftime(start, begin, units="hours"))
        raumsp[i, "endTime"] = abs(difftime(ende, begin, units="hours"))
    }

    return(raumsp)
}



read_raum_sperren15 = function(filename, begin) {
    
    # Read Raumsperren
    raumsp = read.csv(filename, header=TRUE, sep=';')

    # RAUM_CODE;ZUSATZBEZEICHNUNG;SITZPLAETZE;LOKATION;STANDORT;WOCHENTAG;TAG;ZEIT_VON;ZEIT_BIS

    # match times to our time slots
    N2 = length(raumsp$RAUM_CODE)
    get_time2 = function (tag, zeit) {
        return(strptime(paste(tag, zeit), format = "%m/%d/%Y %H:%M"))
    }

    raum_id = raumsp$RAUM_CODE
    raumsp[, "startTime"] = rep(0, N2)
    raumsp[, "endTime"] = rep(0, N2)
    
    for(i in seq(1, N2, 1)) {

        begin_tag = raumsp$TAG[i]
        begin_tag = regmatches(raumsp$TAG[i], regexpr("\\d+\\/\\d+\\/\\d+", raumsp$TAG[i]))
        end_tag = begin_tag
        
        begin_zeit = raumsp$ZEIT_VON[i]
        end_zeit = raumsp$ZEIT_BIS[i]
        
        if(begin_zeit == "0:00") {
            begin_zeit = "0:01"
        }
        
        start = get_time2(begin_tag, begin_zeit)
        ende = get_time2(end_tag, end_zeit)
        
        raumsp[i, "startDate"] = paste(start)
        raumsp[i, "endDate"] = paste(ende)
        
        raumsp[i, "startTime"] = abs(difftime(start, begin, units="hours"))
        raumsp[i, "endTime"] = abs(difftime(ende, begin, units="hours"))
    }

    return(raumsp)
}
