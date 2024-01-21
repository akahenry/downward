#ifndef GREEDY_LOCAL_SEARCH_HEURISTIC_H
#define GREEDY_LOCAL_SEARCH_HEURISTIC_H

#include "pattern_database.h"

#include "../heuristic.h"
#include "post_hoc.h"

#include "types.h"
#include "../plugins/options.h"

enum GreedyTieBreakingOperation
{
    MAX_CONSTRAINT,
    SUM_CONSTRAINTS,
    SUM_SQUARE_CONSTRAINTS
};

namespace pdbs
{
    class GreedyLocalSearch : public PostHoc
    {
    public:
        explicit GreedyLocalSearch(const plugins::Options &opts);
        virtual ~GreedyLocalSearch() = default;

    private:
        float compute_operator_performance(const int operator_id);
        int get_best_operator();
        int compute_times_to_increment(const int operator_id);
        inline bool is_any_restriction_lower_bound_greater_than_zero();
        void update_lower_bounds_with_selected_operator(int operator_id, int times_to_increment);
        void update_operators_with_simple_restrictions();
        int compute_operator_tie_breaking(int operator_id);
        int compute_tie_breaking_max_constraint(int operator_id);
        int compute_tie_breaking_sum_constraint(int operator_id);
        int compute_tie_breaking_sum_square_constraint(int operator_id);
        void delete_restriction(int restriction_id);
        inline bool is_restriction_deleted(int restriction_id);

    protected:
        void compute_post_hoc() override;
        void init_internal_attributes();
        GreedyTieBreakingOperation tie_breaking_operation;
        std::vector<bool> restrictions_valid;
        std::vector<int> non_zero_cost_operators;
        std::vector<int> number_of_relevant_and_valid_restrictions_by_operator;
        int restrictions_with_lower_bound_greater_than_zero;
        std::vector<int> lower_bounds_squared;
        std::vector<int> max_value_pdb_by_operator;
        std::vector<int> pre_computed_times_to_increment_by_operator;
        std::vector<int> pre_computed_performance_denominator_by_operator;
    };
}

#endif
