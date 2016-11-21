#include <vector>
#include <algorithm>
#include <iostream>
#include <math.h>
#include <cmath>
#include <map>
#include <string>
#include <bitset>
#include <tuple>
#include <fstream>
#include <sstream>

class AvidaOrganismDistance {
public:
  std::map<std::string, int> rowAttributeLookup;

  std::map<std::tuple<std::string, std::string>, double> editDistanceMemo;
  std::map<std::tuple<std::string, std::string>, double> simpleMatchingCoeffMemo;

  AvidaOrganismDistance(std::map<std::string, int>& attributeLookup) :
    rowAttributeLookup(attributeLookup) { }
  double getDistance(std::vector<std::string>& row1, std::vector<std::string>& row2) {
    /*
      Given 2 rows (each represents an organism), return a distance between them.
      Here, distance is calculated as follows:
        (0.5)(EditDistance(row1.genome, row2.genome)) + (0.5)(SMC(row1.phenotype, row2.phenotype))
    */
    std::string r1Genome = row1[rowAttributeLookup["genome_sequence"]];
    std::string r2Genome = row2[rowAttributeLookup["genome_sequence"]];
    // Calculated normalized edit distance between r1's genome and r2's genome.
    double gDist = editDistance(r1Genome, r2Genome) / std::max(r1Genome.size(), r2Genome.size());
    std::string r1Phenotype = row1[rowAttributeLookup["phenotype_signature"]];
    std::string r2Phenotype = row2[rowAttributeLookup["phenotype_signature"]];
    double pDist = 1.0 - simpleMatchingCoeff(r1Phenotype, r2Phenotype);
    return (0.5 * gDist) + (0.5 * pDist);
  };

  double editDistance(std::string& a, std::string& b) {
    /*
      Given 2 strings: a & b, calculate edit distance between them.
    */
    auto search = editDistanceMemo.find(std::make_tuple(a, b));
    auto search2 = editDistanceMemo.find(std::make_tuple(b, a));
    if (search != editDistanceMemo.end()) {
      // Found (a, b)
      return search->second;
    } else if (search2 != editDistanceMemo.end()) {
      return search2->second;
    } else {
      // Haven't seen these inputs before. Do calculation and add to lookup table.
      // Create DP table:
      //  * 1 Row for null character + each symbol of a
      //  * 1 Column for null character + each symbol of b
      std::vector<std::vector<int>> table;
      table.resize(a.size() + 1, std::vector<int>(b.size() + 1, 0));
      // Fill out the base case.
      for (size_t i = 0; i < table.size(); i++) {
        table[i][0] = i;
      }
      for (size_t i = 0; i < table[0].size(); i++) {
        table[0][i] = i;
      }
      // Fill out table row by row.
      for (size_t r = 1; r < table.size(); r++) {
        for (size_t c = 1; c < table[r].size(); c++) {
          char achar = a[r - 1];
          char bchar = b[c - 1];
          if (achar == bchar) {
            table[r][c] = table[r - 1][c - 1];
          } else {
            table[r][c] = std::min({table[r - 1][c - 1] + 1, table[r][c - 1] + 1, table[r - 1][c] + 1});
          }
        }
      }
      editDistanceMemo[std::make_tuple(a, b)] = table[table.size() - 1][table[0].size() - 1];
      // editDistanceMemo[std::make_tuple(b, a)] = table[table.size() - 1][table[0].size() - 1];
      return table[table.size() - 1][table[0].size() - 1];
    }

  }

  double simpleMatchingCoeff(std::string& a, std::string& b) {
    /*
      Given strings a & b, find simple matching coefficient.
      Requirements: len(a) == len(b)
                    a and b should both be bit strings.
                    len(a) <= 8
                    len(b) <= 8
     */
     auto search = simpleMatchingCoeffMemo.find(std::make_tuple(a, b));
     if (search != simpleMatchingCoeffMemo.end()) {
       // Found (a, b)
       return search->second;
     } else {
      int m11 = 0, m01 = 0, m10 = 0, m00 = 0;
      std::bitset<8> aBits(a);
      std::bitset<8> bBits(b);
      for (size_t i = 0; i < a.size(); i++) {
        if      (aBits[i] && bBits[i])   m11++;
        else if (aBits[i] && !bBits[i])  m10++;
        else if (!aBits[i] && bBits[i])  m01++;
        else if (!aBits[i] && !bBits[i]) m00++;
      }
      double result = (double)(m11 + m00) / (double)(m11 + m01 + m10 + m00);
      simpleMatchingCoeffMemo[std::make_tuple(a, b)] = result;
      simpleMatchingCoeffMemo[std::make_tuple(b, a)] = result;
      return result;
    }
  }
};

std::vector<std::string> getNextRow(std::istream& str);

int main(int argv, char* argc[]) {
  std::string inputFile;
  std::string outputFile;
  // User provided input? If not, use defaults.
  if (argv > 2) {
    inputFile = argc[1];
    outputFile = argc[2];
  }
  else {
    inputFile = "../testdata/snapshot__pop_2000.csv";
    outputFile = "../testdata/snapshot__pop_2000_dm.csv";
  }
  std::cout << "Computing distance matrix for: " << inputFile << std::endl;
  std::ifstream ifile(inputFile);
  std::vector<std::vector<std::string>> myPopulation = std::vector<std::vector<std::string>>();

  // Capture header information.
  // {"attribute":index}
  std::map<std::string, int> headerLookup;
  if (ifile.peek() != EOF) {
    std::vector<std::string> header = getNextRow(ifile);
    for (size_t i = 0; i < header.size(); i++) headerLookup[header[i]] = i;
  } else {
    std::cout << "This data file is totally empty, wtf?" << std::endl;
    exit(-1);
  }
  // Read in population.
  while (ifile.peek() != EOF)
  {
    myPopulation.push_back(getNextRow(ifile));
  }

  // AvidaOrganismDistance* distMetric = new AvidaOrganismDistance(headerLookup);
  // std::vector<std::vector<double>> distTable; // Table to store pair-wise distances.
  // distTable.resize(myPopulation.size(), std::vector<double>(myPopulation.size(), 0.0));
  // for (size_t i = 0; i < myPopulation.size(); ++i) {
  //   std::cout << "Org: " << i << std::endl;
  //   for (size_t j = i + 1; j < myPopulation.size(); ++j) {
  //     distTable[i][j] = distMetric->getDistance(myPopulation[i], myPopulation[j]);
  //     distTable[j][i] = distTable[i][j];
  //   }
  // }
  AvidaOrganismDistance* distMetric = new AvidaOrganismDistance(headerLookup);
  std::vector<std::vector<double>> genDistTable; // Table to store genotype distances.
  std::vector<std::vector<double>> phenDistTable; // Table to store phenotype distances.
  genDistTable.resize(myPopulation.size(), std::vector<double>(myPopulation.size(), 0.0));
  phenDistTable.resize(myPopulation.size(), std::vector<double>(myPopulation.size(), 0.0));
  for (size_t i = 0; i < myPopulation.size(); ++i) {
    for (size_t j = i + 1; j < myPopulation.size(); ++j) {
      genDistTable[i][j] = distMetric->editDistance(myPopulation[i][headerLookup["genome_sequence"]], myPopulation[j][headerLookup["genome_sequence"]]);
      genDistTable[j][i] = genDistTable[i][j];

      phenDistTable[i][j] = distMetric->simpleMatchingCoeff(myPopulation[i][headerLookup["phenotype_signature"]], myPopulation[j][headerLookup["phenotype_signature"]]);
      phenDistTable[j][i] = phenDistTable[i][j];
    }
  }

  // Output results
  char delim = ',';
  std::ofstream ofile(outputFile);
  for (size_t i = 0; i < myPopulation.size(); ++i) {
    for (size_t j = 0; j < myPopulation.size(); ++j) {
      ofile << genDistTable[i][j] << "|" << phenDistTable[i][j];
      if (j + 1 < myPopulation.size())
        ofile << delim;
    }
    ofile << "\n";
  }
  ofile.close();
  return 0;
}

std::vector<std::string> getNextRow(std::istream& str)
{
  std::vector<std::string> result;
  std::string line;
  std::getline(str, line);

  std::stringstream lineStream(line);
  std::string cell;

  while (std::getline(lineStream, cell, ','))
  {
    result.push_back(cell);
  }
  return result;
}
