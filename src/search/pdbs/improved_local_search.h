#ifndef IMPROVED_LOCAL_SEARCH_HEURISTIC_H
#define IMPROVED_LOCAL_SEARCH_HEURISTIC_H

#include "pattern_database.h"

#include "../heuristic.h"
#include "post_hoc.h"

#include "types.h"
#include "../plugins/options.h"

enum TieBreakingOperation
{
    MAX_CONSTRAINT,
    SUM_CONSTRAINTS,
    SUM_SQUARE_CONSTRAINTS
};

namespace pdbs
{
    class ImprovedLocalSearch : public PostHoc
    {
    public:
        explicit ImprovedLocalSearch(const plugins::Options &opts);
        virtual ~ImprovedLocalSearch() = default;

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
        TieBreakingOperation tie_breaking_operation;
        std::vector<bool> restrictions_valid;
        int restrictions_with_lower_bound_greater_than_zero;
        std::vector<int> lower_bounds_squared;
        int cursor1, cursor2;
    };
}

#endif
