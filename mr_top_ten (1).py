from mrjob.job import MRJob
from mrjob.step import MRStep
import re

regex = re.compile(r"[\w']+")


class MRTopTenWords(MRJob):

    def steps(self):
        return[
	    MRStep(mapper=self.mapper_get_words,combiner=self.combiner_count_words,reducer=self.reducer_sum_counts),
	    MRStep(reducer=self.reducer_sort)]

    #input = .txt or .csv file
    #output = tuple (word, 1)
    def mapper_get_words(self, _, line):
        for word in regex.findall(line):
            yield (word.lower(), 1)

    #combiner to reduce traffic on network, sums next to mapper
    def combiner_count_words(self, word, counts):
        #combines the results close to the map to reduce traffic over network
        yield (word, sum(counts))

    #sum counts
    def reducer_sum_counts(self, word, counts):
        #sums all the counts with the same key
        yield None, (sum(counts), word)

    #input = word count pairs
    #output = sorted top 10 word count pairs
    def reducer_sort(self, _, word_count_pairs):
	test = sorted(word_count_pairs)
        return test[-10:]
	

if __name__ == '__main__':
    MRTopTenWords.run()
