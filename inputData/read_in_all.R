source("read_in_ergebnis.R")
source("read_in_sperren.R")

print("This script mut be called from within the folder inputData!!")

semester = c("15W", "16S")
for(s in semester) {
    
    infile = paste(c("./", s, "/Ergebnis_", s, ".csv"), collapse = "")
    outfile = paste(c("./", s, "/prfg_times.csv"), collapse = "")
    print(s)

    moses = read_in_moses(infile)

    ergebnis = moses[[1]]
    write.csv(ergebnis[,c("PRFG.NUMMER", "TERMIN", "startHours", "endHours", "startDate", "endDate")], file=outfile)
    
    begin = moses[[2]]
    raumfile = paste(c("./", s, "/raum_sperren.csv"), collapse = "")
    
    if(length(grep(pattern="15W", x=s, value=TRUE)) == 1) {
        raumsp = read_raum_sperren15("./15W/Raumsperren.csv", begin)
        write.csv(raumsp[,c("RAUM_CODE", "startTime", "endTime", "startDate", "endDate")], file=raumfile)
    } else {
        raumsp = read_raum_sperren("./16S/Raumsperren.csv", begin)
        write.csv(raumsp[,c("ID_RAUM", "startTime", "endTime", "startDate", "endDate")], file=raumfile)
    }
    
    
}
