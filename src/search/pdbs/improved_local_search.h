#ifndef LOCAL_SEARCH_HEURISTIC_H
#define LOCAL_SEARCH_HEURISTIC_H

#include "pattern_database.h"

#include "../heuristic.h"

#include "../heuristics/ff_heuristic.h"

#include "types.h"

namespace options
{
    class OptionParser;
}

enum Order
{
    SORT,
    RANDOM,
    DEFAULT
};

enum Decrement
{
    BEFORE,
    ITERATIVE,
};

typedef struct
{
    int id;
    int cost;
} Operator;

typedef struct
{
    int id;
    int pricing;
    std::vector<Operator *> operators;
} Restriction;

namespace pdbs
{

    class ImprovedLocalSearch : public Heuristic
    {
        TaskProxy *task_proxy_ptr;

        std::shared_ptr<PDBCollection> heuristics;

        std::vector<Operator> operators;
        std::vector<Restriction> restrictions;
        std::vector<std::vector<Restriction *>> relevant_operators;

        std::vector<int> operator_count;

    protected:
        class BestOperator
        {
        public:
            Operator op;
            int times_to_increment_without_lost;
            double performance;

            BestOperator();
            int get_stride();
        };

        TaskProxy get_task_proxy();

        virtual int compute_heuristic(const State &ancestor_state) override;

        int generate_solution();

        int set_heuristics_pricing(const State &state);

        void initialize_operators();
        void initialize_count_variables();
        void initialize_restrictions();
        void initialize_relevant_operators();

        bool any_pricing_greater_than_zero();
        double sum_operator_performance(Operator op);
        Restriction get_restriction_with_minimum_pricing(Operator op);

    public:
        explicit ImprovedLocalSearch(const options::Options &opts);
        virtual ~ImprovedLocalSearch() = default;
    };
}

#endif
