ergebnis = read.csv("SzenarioergebnisSoSe2016.csv", header=TRUE, sep=';')

ergebnis$startDate = strptime(paste(ergebnis$TERMIN, ergebnis$BEGINN_ZEIT), format = "%m/%d/%Y %H:%M") - 60*30

ergebnis$endDate = strptime(paste(ergebnis$TERMIN, ergebnis$ENDE_ZEIT), format = "%m/%d/%Y %H:%M") - 60*30

filter_exam_times = !unlist(Map(is.na, ergebnis$startDate))

ergebnis = ergebnis[filter_exam_times, ]

# norm to hours
begin = min(ergebnis$startDate)

ergebnis$startHours = abs(difftime(ergebnis$startDate, begin, units="hours"))

ergebnis$endHours = abs(difftime(ergebnis$endDate, begin, units="hours"))

write.csv(ergebnis[,c("PRFG.NUMMER", "startHours", "endHours")], file="prfg_times.csv")

rooms = ergebnis[,grep(pattern="ORT_CODE_.*", x=names(ergebnis), value=TRUE)]
rooms = sort(Reduce(union, rooms))[-1]

raumuebersicht = read.csv("Raumuebersicht.csv", sep=";", header=T)

raeume = raumuebersicht[,c("ID_Raum", "Klausurplaetze_eng")]
