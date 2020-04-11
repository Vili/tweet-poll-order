#Load data and remove any duplicates
polls = read.csv("polls.csv", sep=",", header = FALSE, col.names = c("access_time", "next_token", "poll_id", "options", "votes_1", "votes_2", "votes_3", "votes_4"))
polls = polls[!duplicated(polls$poll_id),]


#Calculate response probabilities for each distinct number of poll options
results = vector("list", 3)
for (i in 2:4) {
	totals = vector(length = i)
	for (j in 1:i) {
		totals[j] = sum(polls[polls$options == i, (4+j)])
	}
	probabilities = totals / sum(totals) * 100
	results[[i-1]] = probabilities
}

#Visualise the results
response_labels = c("1st\noption", "2nd\noption", "3rd\noption", "4th\noption")
for (result in results) {
	barplot(
		result,
		names.arg = response_labels[1:length(result)],
		main = paste("Response distribution in", "Twitter polls\nwith", c("two","three","four")[length(result)-1], "response options"),
		sub = paste("Based on a sample of", format(nrow(polls[polls$options == length(result),]), big.mark=","), "polls tagged #poll\ntweeted 5-11 April 2020 collected by @ViliLe"),
		ylab = "% of responses"
	)
}

