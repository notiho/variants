library(tidyverse)
library(gridExtra)
library(stringr)
library(caret)

metadata_by_kr_number <- read_csv("kr_number_to_title_dynasty_author.csv")

dynasty_times <- read_csv("dynasty_times.csv")

alignments <- read_csv("alignments.csv")

parallel_passages <- read_csv("parallel_passages.csv")

factor_levels_by_profile <- sapply(
  str_split_i(unique(parallel_passages$profile), ":", 2),
  function(x) strsplit(x, ""))
names(factor_levels_by_profile) <- unique(parallel_passages$profile)

# How much text is there from what time?

alignments %>% 
  mutate(wyg_length = str_length(str_remove_all(wyg_aligned, "＿"))) %>%
  select(kr_number, wyg_length) %>%
  left_join(metadata_by_kr_number, by = join_by(kr_number)) %>%
  mutate(dynasty = coalesce(dynasty, "Other")) %>%
  left_join(rownames_to_column(dynasty_times, var = "index"),
            by = join_by("dynasty")) %>%
  mutate(index = as.numeric(index)) %>%
  group_by(dynasty_normalized) %>%
  summarise(num_chars = sum(wyg_length),
            num_works = n(),
            start = first(start),
            end = first(end),
            index = first(index)) %>%
  arrange(index) %>%
  mutate(dynasty_normalized = if_else(dynasty_normalized == "Northern and Southern Dynasties",
                                      "Northern and\\\\Southern Dynasties",
                                      dynasty_normalized)) %>%
  mutate(name_with_date = if_else(is.na(start),
                                  dynasty_normalized,
                                  paste0(
                                         dynasty_normalized, " (",
                                         start, "-", end, ")"))) %>%
  mutate(str = paste(name_with_date, num_works,
                     paste0("\\numprint{", num_chars, "}"),
                     sep = "&")) %>%
  pull(str) %>%
  cat(sep = "\\\\\n")

# Collect some descriptive statistics for the passages 

n_distinct(parallel_passages$profile)
n_distinct(parallel_passages$kr_number)
unique(parallel_passages$profile)

parallel_passages %>%
  count(profile) %>%
  pull(n) %>%
  min()

parallel_passages %>%
  count(profile) %>%
  pull(n) %>%
  max()

parallel_passages %>%
  count(profile) %>%
  pull(n) %>%
  mean()

parallel_passages %>%
  count(profile) %>%
  pull(n) %>%
  sd()

parallel_passages %>%
  group_by(profile) %>%
  summarise(num_docs = n_distinct(kr_number)) %>%
  pull(num_docs) %>%
  mean() %>%
  round(1)

parallel_passages %>%
  group_by(profile) %>%
  summarise(num_docs = n_distinct(kr_number)) %>%
  pull(num_docs) %>%
  sd() %>%
  round(1)

parallel_passages %>%
  group_by(kr_number) %>%
  summarise(num_profiles = n_distinct(profile)) %>%
  count(num_profiles)

# How imbalanced are the datasets for different profiles?
freq_of_dominant_form <- parallel_passages %>%
  count(profile, b) %>%
  group_by(profile) %>%
  mutate(freq = n / sum(n)) %>%
  summarise(highest_freq = max(freq)) %>%
  pull(highest_freq)

(100 * (freq_of_dominant_form %>% max())) %>% round(1)
(100 * (freq_of_dominant_form %>% mean())) %>% round(1)
(100 * (freq_of_dominant_form %>% sd())) %>% round(1)


# First experiment

predictions_by_doc <- read_csv("regression_predictions_by_document.csv")

highest_prob_predictions_by_doc <- predictions_by_doc %>%
  group_by(target_layer, index) %>%
  slice_max(probability) %>%
  ungroup()

get_overall_accuracy <- function(profile, predictions, targets) {
  predictions <- factor(predictions, levels = factor_levels_by_profile[[profile]])
  targets <- factor(targets, levels = factor_levels_by_profile[[profile]])
  list(confusionMatrix(predictions, targets)$overall)
}

# Best configuration for training: layer 12
highest_prob_predictions_by_doc %>%
  group_by(target_layer, profile, kr_number) %>%
  summarise(overall_accuracy = get_overall_accuracy(first(profile), prediction, target)) %>%
  unnest_wider(overall_accuracy) %>%
  ungroup() %>%
  group_by(target_layer) %>%
  mutate(AccuracyPValue = p.adjust(AccuracyPValue, method = "bonferroni")) %>%
  summarise(num_above_nir = sum(AccuracyPValue < 0.05),
            mean_overall_accuracy = mean(Accuracy)) %>%
  arrange(desc(num_above_nir), desc(mean_overall_accuracy)) %>%
  print(n = 30)

accuracy_by_profile_doc <- highest_prob_predictions_by_doc %>%
  filter(target_layer == 11) %>%
  group_by(profile, kr_number) %>%
  summarise(overall_accuracy = get_overall_accuracy(first(profile), prediction, target)) %>%
  unnest_wider(overall_accuracy) %>%
  ungroup() %>%
  mutate(AccuracyPValue = p.adjust(AccuracyPValue, method = "bonferroni"),
         above_nir = AccuracyPValue < 0.05)


# How many above nir?
accuracy_by_profile_doc %>%
  count(above_nir)

(100 * 77 / (77 + 161)) %>% round(1)

# How many profiles with at least one document above nir?
accuracy_by_profile_doc %>%
  group_by(profile) %>%
  summarise(any_above_nir = any(above_nir)) %>%
  count(any_above_nir)

(100 * 45 / (45 + 63)) %>% round(1)


# Context for two unexpected cases
highest_prob_predictions_by_doc %>%
  filter(target_layer == 11 & profile == "爾:尓爾" & kr_number == "KR3k0012") %>%
  mutate(l_a = str_sub(parallel_passages$l_a[index + 1], -3, -1),
         r_a = str_sub(parallel_passages$r_b[index + 1], 1, 3)) %>%
  arrange(target) %>%
  print(n = 200)

highest_prob_predictions_by_doc %>%
  filter(target_layer == 11 & profile == "聲:声聲" & kr_number %in% c("KR4c0044", "KR4c0049")) %>%
  mutate(l_a = str_sub(parallel_passages$l_a[index + 1], -1, -1),
         r_a = str_sub(parallel_passages$r_b[index + 1], 1, 1)) %>%
  count(target, l_a, kr_number) %>%
  arrange(desc(n))

# Accuracy
(100 * (accuracy_by_profile_doc %>%
  filter(above_nir) %>%
  pull(Accuracy) %>%
  min())) %>%
  round(1)

(100 * (accuracy_by_profile_doc %>%
          filter(above_nir) %>%
          pull(Accuracy) %>%
          max())) %>%
  round(1)


(100 * (accuracy_by_profile_doc %>%
          filter(above_nir) %>%
          pull(Accuracy) %>%
          mean())) %>%
  round(1)

(100 * (accuracy_by_profile_doc %>%
          filter(above_nir) %>%
          pull(Accuracy) %>%
          sd())) %>%
  round(1)

# Table for appendix
accuracy_by_profile_doc %>%
  group_by(profile) %>%
  summarise(n_above_nir = sum(above_nir),
            total = n()) %>%
  arrange(desc(total)) %>%
  rownames_to_column("index") %>%
  mutate(tex = paste0(str_replace_all(profile, ":", "$\\\\leftrightarrow$"), "&", n_above_nir, "/", total, if_else(as.integer(index) %% 2 == 0, "\\\\", "&"))) %>%
  pull(tex) %>%
  cat(sep = "\n")

# Second experiment
predictions_cross_docs <- read_csv("regression_predictions_cross_document.csv")

highest_prob_predictions_cross_docs <- predictions_cross_docs %>%
  group_by(profile, train_kr_number, index) %>%
  slice_max(probability) %>%
  ungroup()

accuracy_cross_docs <- highest_prob_predictions_cross_docs %>%
  left_join(accuracy_by_profile_doc,
            by = join_by(profile, train_kr_number == kr_number)) %>%
  left_join(accuracy_by_profile_doc,
            by = join_by(profile, test_kr_number == kr_number),
            suffix = c(".train", ".test")) %>%
  filter(above_nir.train & above_nir.test) %>%
  group_by(profile, train_kr_number, test_kr_number) %>%
  summarise(overall_accuracy = get_overall_accuracy(first(profile), prediction, target)) %>%
  unnest_wider(overall_accuracy) %>%
  ungroup() %>%
  mutate(AccuracyPValue = p.adjust(AccuracyPValue, method = "bonferroni"),
         above_nir = AccuracyPValue < 0.05)

# Generate table
accuracy_cross_docs %>%
  group_by(profile) %>%
  summarise(above_nir = sum(above_nir), total = n()) %>%
  arrange(desc(total)) %>%
  mutate(tex = paste0(str_replace_all(profile, ":", "$\\\\leftrightarrow$"), "&", above_nir, "/", total)) %>%
  pull(tex) %>%
  cat(sep = "\\\\\n")

# Does time difference have an effect on transferability?
cross_docs_same_dynasty_vs_above_nir <- accuracy_cross_docs %>%
  filter(profile == "厯:暦歴" | profile == "歴:暦歴") %>%
  left_join(metadata_by_kr_number,
            by = join_by(train_kr_number == kr_number)) %>%
  left_join(metadata_by_kr_number,
            by = join_by(test_kr_number == kr_number),
            suffix = c(".train", ".test")) %>%
  mutate(same_dynasty = dynasty.train == dynasty.test)

chisq.test(cross_docs_same_dynasty_vs_above_nir$same_dynasty, cross_docs_same_dynasty_vs_above_nir$above_nir)

cross_docs_same_dynasty_vs_above_nir %>% 
  count(same_dynasty, above_nir)

(100 * 81 / (13 + 81)) %>% round(1)
(100 * 40 / (10 + 40)) %>% round(1)

# Accuracy of 暦歴 profiles

accuracy_cross_docs %>%
  filter(profile == "厯:暦歴" | profile == "歴:暦歴") %>%
  filter(above_nir) %>%
  pull(Accuracy) %>%
  min()

accuracy_cross_docs %>%
  filter(profile == "厯:暦歴" | profile == "歴:暦歴") %>%
  filter(above_nir) %>%
  pull(Accuracy) %>%
  max()

accuracy_cross_docs %>%
  filter(profile == "厯:暦歴" | profile == "歴:暦歴") %>%
  filter(above_nir) %>%
  pull(Accuracy) %>%
  mean()

accuracy_cross_docs %>%
  filter(profile == "厯:暦歴" | profile == "歴:暦歴") %>%
  filter(above_nir) %>%
  pull(Accuracy) %>%
  sd()

learnable_li_li <- accuracy_by_profile_doc %>%
  filter(profile == "厯:暦歴" | profile == "歴:暦歴") %>%
  filter(above_nir) %>%
  pull(kr_number)
unique(learnable_li_li)

# Does training with more documents help prediction of 暦歴?
predictions_li_li <- read_csv("predictions_li_li.csv")

highest_prob_predictions_li_li <- predictions_li_li %>%
  group_by(index) %>%
  slice_max(probability) %>%
  ungroup()

accuracy_li_li <- highest_prob_predictions_li_li %>%
  group_by(test_kr_number) %>%
  summarise(overall_accuracy = get_overall_accuracy("厯:暦歴", prediction, target)) %>%
  unnest_wider(overall_accuracy)

mean(accuracy_li_li$Accuracy)
sd(accuracy_li_li$Accuracy)
