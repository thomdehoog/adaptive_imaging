library(data.table)
library(ggplot2)
library(flextable)

INTERIM_PATH <- ""

DXY.UM <- 0.11
DT.SEC <- 0.10
CUTTING <- 50
MAXT.SEC <- 10

## HELPERS

igam <- function(x, y){
  model <- scam::scam(y ~ s(x, bs = 'mpi'))
  return(model$fitted)
}

sample_derivative <- function(xs, ys, xq, order=1){
  spline_model <- splinefun(xs, ys)
  return(spline_model(xq, deriv=order))
}

## Edge, Minor

EDGE_MINOR_RECOIL_PATH <- file.path(INTERIM_PATH, "80umMinorAxisJunctionsDataSet_sendToGreg20230208", "recoil.csv")

edge.minor.dt <- fread(EDGE_MINOR_RECOIL_PATH)
edge.minor.meta.dt <- edge.minor.dt[, .N, by = .(filename, strain)]
# edge.minor.meta.dt[, uid := 1:nrow(edge.minor.meta.dt)]
edge.minor.meta.dt[,cutting_type := "edge"]
edge.minor.meta.dt[,axis := "minor"]
edge.minor.meta.dt[,embryo := NA_character_]
setkeyv(edge.minor.meta.dt, "filename")

# edge.minor.dt[,uid:=edge.minor.meta.dt[filename, uid]]
edge.minor.dt[,cutting_type:=edge.minor.meta.dt[filename, cutting_type]]
edge.minor.dt[,axis:=edge.minor.meta.dt[filename, axis]]
edge.minor.dt[,embryo := NA_character_]
# edge.minor.dt[,filename:=NULL]
# setkeyv(edge.minor.meta.dt, "uid")

# Edge, Major
EDGE_MAJOR_RECOIL_PATH <- file.path(INTERIM_PATH, "80um_MajorAxisJunctionsCuts_KymographDataSet_sendToGreg20230213", "recoil.csv")

edge.major.dt <- fread(EDGE_MAJOR_RECOIL_PATH)
edge.major.meta.dt <- edge.major.dt[, .N, by = .(filename, strain)]
# edge.major.meta.dt[, uid := 1:nrow(edge.major.meta.dt)]
edge.major.meta.dt[,cutting_type := "edge"]
edge.major.meta.dt[,axis := "major"]
edge.major.meta.dt[,embryo := NA_character_]
setkeyv(edge.major.meta.dt, "filename")

# edge.major.dt[,uid:=edge.major.meta.dt[filename, uid]]
edge.major.dt[,cutting_type:=edge.major.meta.dt[filename, cutting_type]]
edge.major.dt[,axis:=edge.major.meta.dt[filename, axis]]
edge.major.dt[,embryo := NA_character_]
# edge.major.dt[,filename:=NULL]
# setkeyv(edge.major.meta.dt, "uid")

# Apical
APICAL_RECOIL_PATH <- file.path(INTERIM_PATH, "80um_ApicalSurfaceCuts_KymographDataset_sendToGreg20230213", "recoil.csv")

apical.dt <- fread(APICAL_RECOIL_PATH)
apical.dt[axis == "MajorAxisKymograph", axis := "major"]
apical.dt[axis == "MinorAxisKymograph", axis := "minor"]
apical.meta.dt <- apical.dt[, .N, by = .(filename, strain, embryo, axis)]
apical.meta.dt[,cutting_type := "apical"]
setkeyv(apical.meta.dt, "filename")
# 
# edge.major.dt[,uid:=edge.major.meta.dt[filename, uid]]
apical.dt[,cutting_type:=apical.meta.dt[filename, cutting_type]]
# edge.major.dt[,axis:=edge.major.meta.dt[filename, axis]]
# edge.major.dt[,filename:=NULL]
# setkeyv(edge.major.meta.dt, "uid")

meta.dt <- rbindlist(list(edge.major.meta.dt, edge.minor.meta.dt, apical.meta.dt), use.names=TRUE)
meta.dt[,uid := seq.int(nrow(meta.dt))]
all_paths <- basename(c(Sys.glob(file.path(INTERIM_PATH, "*/*/*/*tif")), Sys.glob(file.path(INTERIM_PATH, "*/*/*tif"))))

## Check with have everything
all(meta.dt[,filename] %in% all_paths)

dt <- rbindlist(list(edge.major.dt, edge.minor.dt, apical.dt), use.names = TRUE)
setkeyv(meta.dt, "filename")

dt[,uid:=meta.dt[filename, uid]]
dt[,filename:=NULL]
setkeyv(meta.dt, "uid")

dt[frame <  CUTTING, event := "before"]
dt[frame == CUTTING, event := "cutting"]
dt[frame >  CUTTING, event := "after"]

dt[,s.um := s * DXY.UM]
dt[,time.sec := (frame - CUTTING) * DT.SEC]
dt[,s.um := mean(s.um), by=.(uid, side, frame)]

dt <- unique(dt[,.(uid, strain, event, side, time.sec, s.um)])

dt[,baseline.um := median(s.um[event == "before"]),
   by = .(uid, side)]
dt[,side := factor(side)]
dt[,uid := factor(uid)]
dt[,strain := factor(strain)]
setorder(dt, uid, side, time.sec)

ggplot(data=dt,
       mapping = aes(x = time.sec, y = s.um - baseline.um,
                     col = side,
                     group = uid:side))+
  geom_vline(xintercept = 0, linetype="dashed")+
  geom_hline(yintercept = 0, linetype="dashed")+
  geom_line()+
  geom_point()+
  facet_wrap(~uid)

dt[time.sec < 0 , utime.sec := time.sec, by=.(uid, side, s.um)]
dt[time.sec > 0 & time.sec < MAXT.SEC, utime.sec := median(time.sec), by=.(uid, side, s.um)]
dt[time.sec == MAXT.SEC, utime.sec := time.sec, by=.(uid, side, s.um)]

udt <- dt
udt[,time.sec := NULL]
udt <- unique(udt)

ggplot(data=udt)+
  geom_vline(xintercept = 0, linetype="dashed")+
  geom_hline(yintercept = 0, linetype="dashed")+
  geom_point(aes(x = utime.sec, y = s.um - baseline.um,
                 col = side,
                 group = uid:side))+
  facet_wrap(~uid)

udt[,disp.um := abs(s.um -baseline.um)]
ggplot(data=udt[utime.sec >= 0],
       mapping=aes(x = utime.sec, y = disp.um,
                   col = side,
                   group = uid:side))+
  geom_vline(xintercept = 0, linetype="dashed")+
  geom_hline(yintercept = 0, linetype="dashed")+
  geom_point()+
  # geom_smooth()+
  scale_x_continuous(trans='log10')+
  scale_y_continuous(trans='log10')+
  facet_wrap(~uid)

times_seq <- seq(0, MAXT.SEC, by=DT.SEC)
disp.dt <- udt[,approx(utime.sec, disp.um, times_seq), by=.(uid, side, strain)]
setnames(disp.dt, "x", "time.sec")
setnames(disp.dt, "y", "disp.um")
disp.dt[,total.disp.um := sum(disp.um), by=.(uid, time.sec)]
disp.dt[,side:=NULL]
disp.dt[,disp.um:=NULL]
disp.dt <- unique(disp.dt)

disp.dt <- merge(disp.dt, meta.dt[,.(uid=as.factor(uid), cutting_type, axis, strain)], by=c("uid", "strain"))

ggplot(data = disp.dt,
       mapping = aes(x=time.sec, y=total.disp.um))+
  geom_point(aes(group=uid, color=strain), alpha=0.2)+
  geom_line(aes(group=uid, color=strain), alpha=0.2)+
  geom_smooth(aes(color=strain), size=2.0)+
  facet_grid(axis~cutting_type)

ggplot(data = disp.dt[uid %in% sample(unique(uid), 36) ],
       mapping = aes(x=time.sec, y=total.disp.um))+
  geom_point(aes(group=uid, color=strain))+
  geom_line(aes(group=uid, color=strain))+
  geom_smooth(color="black", method=scam::scam, formula = y ~ s(x, bs = "mpi"))+
  facet_wrap(~uid)


ggplot(data=disp.dt[,
                    .(mean=mean(total.disp.um), sem=sd(total.disp.um)/sqrt(.N)),
                    by=.(time.sec, strain, cutting_type, axis)])+
  geom_line(aes(x=time.sec, y=mean, color=strain), size=1.25)+
  # scale_x_continuous(trans='log10')+
  # scale_y_continuous(trans='log10')+
  geom_errorbar(aes(x=time.sec, y=mean, ymin=mean-1.96*sem, ymax=mean+1.96*sem, col=strain))+
  facet_grid(axis~cutting_type)+
  xlab("Time [sec]")+
  ylab("Avg. Displacement [um]")

ggplot(data=disp.dt[,.(mean=mean(total.disp.um), sem=sd(total.disp.um)/sqrt(.N)),
                    by=.(time.sec, strain, cutting_type)])+
  geom_line(aes(x=time.sec, y=mean, color=strain), size=1.25)+
  # scale_x_continuous(trans='log10')+
  # scale_y_continuous(trans='log10')+
  geom_errorbar(aes(x=time.sec, y=mean, ymin=mean-1.96*sem, ymax=mean+1.96*sem, col=strain))+
  facet_wrap(~cutting_type)+
  xlab("Time [sec]")+
  ylab("Avg. Displacement [um]")

disp.dt[,fit := igam(time.sec, total.disp.um), by=uid]
disp.dt[,fit.deriv := sample_derivative(time.sec, fit, time.sec), by=uid]

ggplot(data=disp.dt[uid %in% sample(unique(uid), 36)])+
  geom_point(aes(x=time.sec, y=total.disp.um))+
  geom_line(aes(x=time.sec, y=fit), col='red')+
  facet_wrap(~uid)

ggplot(data=disp.dt[uid %in% sample(unique(uid), 36)])+
  geom_line(aes(x=time.sec, y=fit.deriv), col='red')+
  facet_wrap(~uid)

recoil.dt <- disp.dt[,.(recoil=mean(fit.deriv[1])), by=.(uid, strain, cutting_type, axis)]

cut_labels <- c(apical = "Apical", edge = "Edge")
axis_labels <- c(major="Major axis", minor="Minor axis")
gp <- ggplot(data=recoil.dt)+
  geom_boxplot(aes(x=strain, y=recoil, fill=strain),
               outlier.shape = NA,
              )+
  geom_jitter(aes(x=strain, y=recoil,
                  shape=axis),
              size=2,
              position = position_jitter(0.1))+
  scale_color_brewer(palette="Dark2")+
  scale_shape_manual(values=c(15, 3), name="Junction Orientation", labels=axis_labels)+
  facet_wrap(~cutting_type, labeller = as_labeller(cut_labels))+
  guides(fill="none")+
  xlab("")+
  ylab("Recoil [µm/s]")+
  theme_gray(base_size = 12)+
  theme(legend.position = "top")

print(gp)
ggsave("fig2_recoil_portrait.pdf", width = 15/2, height = 17/2, dpi=600)

gp +
  geom_jitter(aes(x=strain, y=recoil,
                  shape=axis),
              size=2,
              position = position_jitter(0.2))+
  scale_x_discrete(limits=rev) + 
  coord_flip()

ggsave("fig2_recoil_landscape.pdf", width = 25/2, height = 6/2, dpi=600)

model <- recoil.dt[,lm(recoil ~ cutting_type + cutting_type / strain)]
summary(model)

model_flx <- as_flextable(model)
format_scientific <- function(x) {
  formatC(x, format = "e", digits = 2)
}
model_flx <- set_formatter(model_flx, "p.value"=format_scientific)
save_as_docx(model_flx, path="recoil_model_table.docx")

## Stratifiying for axis as well
gp <- ggplot(data=recoil.dt)+
  geom_boxplot(aes(x=strain, y=recoil, fill=strain),
               outlier.shape = NA,
  )+
  geom_jitter(aes(x=strain, y=recoil,
                  shape=axis),
              size=2,
              position = position_jitter(0.1))+
  scale_color_brewer(palette="Dark2")+
  scale_shape_manual(values=c(15, 3), name="Junction Orientation", labels=axis_labels)+
  facet_grid(axis~cutting_type, labeller = as_labeller(c(cut_labels, axis_labels)))+
  guides(fill="none")+
  xlab("")+
  ylab("Recoil [µm/s]")+
  theme_gray(base_size = 12)+
  theme(legend.position = "top")
print(gp)
ggsave("fig2_recoil_portrait_stratification=cutting+axis.pdf", width = 15/2, height = 17/2, dpi=600)

gp +
  geom_jitter(aes(x=strain, y=recoil,
                  shape=axis),
              size=2,
              position = position_jitter(0.2))+
  scale_x_discrete(limits=rev) + 
  coord_flip()

ggsave("fig2_recoil_landscape_stratification=cutting+axis.pdf.pdf", width = 25/2, height = 12/2, dpi=600)


model2 <- recoil.dt[,lm(recoil ~ cutting_type*axis + cutting_type*axis / strain)]
summary(model2)

model2_flx <- as_flextable(model2)
model2_flx <- set_formatter(model2_flx, "p.value"=format_scientific)
save_as_docx(model2_flx, path="recoil_model_both_factors_table.docx")
