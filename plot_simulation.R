library(ggplot2)
library(cowplot)

nouns_dataset = read.csv("C:/Users/Tim/Documents/Example_based_backup/endterm_results/after_SUBTLEX_exceptions_improvements/bugfixed/test_run_nouns_k1_w0_mO_n3_g365_in800_out200_mem15.csv")
adj_dataset = read.csv("C:/Users/Tim/Documents/Example_based_backup/endterm_results/after_SUBTLEX_exceptions_improvements/bugfixed/test_run_adjectives_k1_w1_mO_n3_g365_in200_out30_mem15.csv")

plot1 = ggplot(nouns_dataset, aes(Generation, y = Percentage, color = Measure)) + 
  geom_smooth(aes(y = Accuracy, col = "Accuracy")) + 
  geom_smooth(aes(y = perc_het_instead_of_de, col = "'het' instead of 'de'")) + 
  geom_smooth(aes(y = perc_de_instead_of_het, col = "'de' instead of 'het'")) + 
  theme(legend.position="bottom", legend.title=element_blank(), axis.title.x = element_text(size=18), axis.text.x  = element_text(size=16), axis.title.y = element_text(size=18), axis.text.y = element_text(size = 16), legend.text = element_text(size = 16)) + 
  scale_color_manual(values=c("red", "#56B4E9", "#999999"), 
                     breaks=c("Accuracy", "'het' instead of 'de'", "'de' instead of 'het'"),
                     labels=c("Accuracy", "% het>de", "% de>het"))

plot2 = ggplot(adj_dataset, aes(Generation, y = Percentage, color = Measure)) + 
  geom_smooth(aes(y = Accuracy, col = "Accuracy")) + 
  geom_smooth(aes(y = perc_zero_instead_of_schwa, col = "'zero' instead of 'schwa'")) + 
  geom_smooth(aes(y = perc_schwa_instead_of_zero, col = "'schwa' instead of 'zero'")) +
  theme(legend.position="bottom", legend.title=element_blank(), axis.title.x = element_text(size=18), axis.text.x  = element_text(size=16), axis.title.y = element_text(size=18), axis.text.y = element_text(size = 16), legend.text = element_text(size = 16)) + 
  scale_color_manual(values=c("red", "#56B4E9", "#999999"), 
                     breaks=c("Accuracy", "'zero' instead of 'schwa'", "'schwa' instead of 'zero'"),
                     labels=c("Accuracy", "% -ø > -??", "% -?? > -ø"))

plot_grid(plot1, plot2, align = "v", ncol = 1)