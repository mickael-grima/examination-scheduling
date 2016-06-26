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
    write.csv(ergebnis[,c("PRFG.NUMMER", "startHours", "endHours", "startDate", "endDate")], file=outfile)
}
# begin = moses[[2]]
# sperren_file = "./Data/RaumsperrenSoSe2016.csv"
# raumsp = read_raum_sperren(sperren_file, begin)
# 
# write.csv(raumsp[,c("ID_RAUM", "startTime", "endTime", "startDate", "endDate")], file="Data/raum_sperren.csv")
