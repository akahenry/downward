#ifndef LOCAL_SEARCH_HEURISTIC_H
#define LOCAL_SEARCH_HEURISTIC_H

#include "pattern_database.h"

#include "../heuristic.h"

#include "types.h"
#include "../plugins/options.h"

namespace pdbs
{

    class ImprovedLocalSearch : public Heuristic
    {
        int seed;

        std::shared_ptr<PDBCollection> pdbs;

        // operadores
        std::vector<int> operators;
        std::vector<int> operator_cost;
        std::vector<int> operator_count;

        // restrições
        std::vector<std::vector<int>> restrictions;
        std::vector<std::vector<int>> restriction_operator;
        std::vector<std::vector<int>> restrictions_landmarks;

        // vetores auxiliares de memória
        std::vector<int> solution;
        std::vector<int> value_pdbs;
        std::vector<int> lower_bounds;
        std::vector<int> restriction_order;

    protected:
        virtual int compute_heuristic(const State &ancestor_state) override;

        int generate_solution(const State &state);

        int set_value_pdbs(const State &state);

        void get_restrictions();

        void print_info();

    public:
        explicit ImprovedLocalSearch(const plugins::Options &opts);
        virtual ~ImprovedLocalSearch() = default;
    };
}

#endif
