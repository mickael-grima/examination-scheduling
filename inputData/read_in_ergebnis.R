

#read in moses result
read_in_moses = function(filename) {
    
    ergebnis = read.csv(filename, header=TRUE, sep=';')

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

    slots_begin = c("07:30", "10:15", "13:00", "15:45")
    slots_ende = c("10:15", "13:00", "15:45", "18:30")

    get_time = function (termin, zeit) {
        return(strptime(paste(termin, zeit), format = "%m/%d/%Y %H:%M"))
    }

    for(i in seq(1, N, 1)) {
        termin = ergebnis$TERMIN[i]
        begin = get_time(termin, ergebnis$BEGINN_ZEIT[i])
        ende = get_time(termin, ergebnis$ENDE_ZEIT[i])
        mid = begin + 0.5*(ende - begin)
        
        for(j in seq(length(slots_begin))) {
            if(difftime(mid, get_time(termin, slots_begin[j])) >= 0 && difftime(mid, get_time(termin, slots_ende[j])) <= 0) {
                ergebnis[i, "startDate"] = paste(get_time(termin, slots_begin[j]))
                ergebnis[i, "endDate"] = paste(get_time(termin, slots_ende[j]))
                ergebnis[i, "midDate"] = paste(mid)
                break
            }
        }
    }


    # norm to hours
    begin = min(ergebnis$startDate)

    ergebnis$startHours = abs(difftime(ergebnis$startDate, begin, units="hours"))
    ergebnis$endHours = abs(difftime(ergebnis$endDate, begin, units="hours"))
    ergebnis$midHours = abs(difftime(ergebnis$midDate, begin, units="hours"))
    ergebnis$diffWeeks = round(difftime(ergebnis$startDate, begin, units="weeks"))

    return(list(ergebnis, begin))
}

