source("read_in_ergebnis.R")
source("read_in_sperren.R")

print("This script mut be called from within the folder inputData!!")

semester = "16S"
infile = paste(c("./", semester, "/Ergebnis_", semester, ".csv"), collapse = "")
outfile = paste(c("./", semester, "/prfg_times.csv"), collapse = "")
print(semester)

moses = read_in_moses(infile)

ergebnis = moses[[1]]
write.csv(ergebnis[,c("PRFG.NUMMER", "startHours", "endHours", "startDate", "endDate")], file=outfile)

# begin = moses[[2]]
# sperren_file = "./Data/RaumsperrenSoSe2016.csv"
# raumsp = read_raum_sperren(sperren_file, begin)
# 
# write.csv(raumsp[,c("ID_RAUM", "startTime", "endTime", "startDate", "endDate")], file="Data/raum_sperren.csv")
