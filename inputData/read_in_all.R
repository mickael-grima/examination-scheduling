source("read_in_ergebnis.R")
moses = read_in_moses()
ergebnis = moses[[1]]
begin = moses[[2]]


source("read_in_sperren.R")
raumsp = read_raum_sperren(begin)

write.csv(ergebnis[,c("PRFG.NUMMER", "startHours", "endHours", "startDate", "endDate")], file="Data/prfg_times.csv")

write.csv(raumsp[,c("ID_RAUM", "startTime", "endTime", "startDate", "endDate")], file="Data/raum_sperren.csv")
