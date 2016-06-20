ergebnis = read.csv("./Data/SzenarioergebnisSoSe2016.csv", header=TRUE, sep=';')

#filter na exams
ergebnis = ergebnis[!is.na(ergebnis$BEGINN_ZEIT), ]
ergebnis = ergebnis[!is.na(ergebnis$ENDE_ZEIT), ]
ergebnis = ergebnis[!is.na(strptime(paste(ergebnis$TERMIN, ergebnis$BEGINN_ZEIT), format = "%m/%d/%Y %H:%M")), ]

#ergebnis$startDate = strptime(paste(ergebnis$TERMIN, ergebnis$BEGINN_ZEIT), format = "%m/%d/%Y %H:%M") - 60*30
#ergebnis$endDate = strptime(paste(ergebnis$TERMIN, ergebnis$ENDE_ZEIT), format = "%m/%d/%Y %H:%M") + 60*30
# filter_exam_times = !unlist(Map(is.na, ergebnis$startDate))
# ergebnis = ergebnis[filter_exam_times, ]

# match times to our time slots
N = length(ergebnis$TERMIN)

termine = unique(ergebnis$TERMIN)

slot_begin_1 = "08:00"
slot_ende_1 = "11:30"
slot_begin_2 = "11:30"
slot_ende_2 = "15:00"
slot_begin_3 = "15:00"
slot_ende_3 = "18:30"

get_time = function (termin, zeit) {
    return(strptime(paste(termin, zeit), format = "%m/%d/%Y %H:%M"))
}

for(i in seq(1, N, 1)) {
    termin = ergebnis$TERMIN[i]
    begin = get_time(termin, ergebnis$BEGINN_ZEIT[i])
    ende = get_time(termin, ergebnis$ENDE_ZEIT[i])
    mid = begin + 0.5*(ende - begin)
    
    if(difftime(mid, get_time(termin, slot_begin_1)) >= 0 && difftime(mid, get_time(termin, slot_ende_1)) <= 0) {
        ergebnis[i, "startDate"] = paste(get_time(termin, slot_begin_1))
        ergebnis[i, "endDate"] = paste(get_time(termin, slot_ende_1))
        ergebnis[i, "midDate"] = paste(mid)
    } else if(difftime(mid, get_time(termin, slot_begin_2)) >= 0 && difftime(mid, get_time(termin, slot_ende_2)) <= 0) {
        ergebnis[i, "startDate"] = paste(get_time(termin, slot_begin_2))
        ergebnis[i, "endDate"] = paste(get_time(termin, slot_ende_2))
        ergebnis[i, "midDate"] = paste(mid)
    } else if(difftime(mid, get_time(termin, slot_begin_3)) >= 0 && difftime(mid, get_time(termin, slot_ende_3)) <= 0) {
        ergebnis[i, "startDate"] = paste(get_time(termin, slot_begin_3))
        ergebnis[i, "endDate"] = paste(get_time(termin, slot_ende_3))
        ergebnis[i, "midDate"] = paste(mid)
    } else {
        print("Schmarrn!")
        print(begin)
        print(ende)
        print(mid)
    }
}


# norm to hours
begin = min(ergebnis$startDate)

ergebnis$startHours = abs(difftime(ergebnis$startDate, begin, units="hours"))
ergebnis$endHours = abs(difftime(ergebnis$endDate, begin, units="hours"))
ergebnis$midHours = abs(difftime(ergebnis$midDate, begin, units="hours"))
ergebnis$diffWeeks = round(difftime(ergebnis$startDate, begin, units="weeks"))

write.csv(ergebnis[,c("PRFG.NUMMER", "startHours", "endHours", "midHours", "diffWeeks")], file="Data/prfg_times.csv")



# 
# rooms = ergebnis[,grep(pattern="ORT_CODE_.*", x=names(ergebnis), value=TRUE)]
# rooms = sort(Reduce(union, rooms))[-1]
# 
# raumuebersicht = read.csv("Data/Raumuebersicht.csv", sep=";", header=T)
# raeume = raumuebersicht[,c("ID_Raum", "Klausurplaetze_eng")]


# Read Raumsperren
raumsp = read.csv("./Data/RaumsperrenSoSe2016.csv", header=TRUE, sep=';')

#ID_RAUM;ZUSATZBEZEICHNUNG;WOCHENTAG;TAG;ZEIT_VON;ZEIT_BIS;BIS_TAG;BIS_ZEIT

# match times to our time slots
N2 = length(raumsp$ID_RAUM)

slot_begin_1 = "08:00"
slot_ende_1 = "11:30"
slot_begin_2 = "11:30"
slot_ende_2 = "15:00"
slot_begin_3 = "15:00"
slot_ende_3 = "18:30"

get_time2 = function (tag, zeit) {
    return(strptime(paste(tag, zeit), format = "%d/%m/%Y %H:%M"))
}

raum_id = raumsp$ID_RAUM
raumsp[, "startTime"] = rep(0, N2)
raumsp[, "endTime"] = rep(0, N2)

for(i in seq(1, N2, 1)) {
    print(i)
    begin_tag = raumsp$TAG[i]
    end_tag = raumsp$BIS_TAG[i]
    
    if( is.na(end_tag) ) { end_tag = begin_tag }
    
    begin_zeit = raumsp$ZEIT_VON[i]
    end_zeit = raumsp$ZEIT_BIS[i]
    print(end_zeit)
    if( is.na(end_zeit) ) { end_zeit = raumsp$BIS_ZEIT[i] }
    
    print(end_zeit)
    
    start = get_time2(begin_tag, begin_zeit)
    ende = get_time2(end_tag, end_zeit)
    print(start)
    print(ende)
    
    raumsp[i, "startTime"] = abs(difftime(start, begin, units="hours"))
    raumsp[i, "endTime"] = abs(difftime(ende, begin, units="hours"))
}

write.csv(raumsp[,c("ID_RAUM", "startTime", "endTime")], file="Data/raum_sperren.csv")
