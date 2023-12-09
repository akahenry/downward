#ifndef LOCAL_SEARCH_HEURISTIC_H
#define LOCAL_SEARCH_HEURISTIC_H

#include "pattern_database.h"

#include "../heuristic.h"

#include "post_hoc.h"

#include "../heuristics/ff_heuristic.h"

#include "types.h"
#include "../plugins/options.h"

enum class Order
{
    SORT,
    RANDOM,
    DEFAULT
};

enum class Decrement
{
    BEFORE,
    ITERATIVE,
};

namespace pdbs
{

    class LocalSearch : public PostHoc
    {
        const size_t iterations;

        Order op_order;
        Order res_order;

        Decrement decrement_mode;

        int seed;

        bool use_ff;
        bool use_preferred;

        std::vector<int> restriction_order;

        std::shared_ptr<ff_heuristic::FFHeuristic> hff;
        std::shared_ptr<std::vector<bool>> hff_prefops;

        void setup_restriction_ordering();

        template <typename T>
        static void random_shuffle(std::vector<T> vec)
        {
            // Solution found in https://stackoverflow.com/a/45014073
            std::random_device rd;
            std::mt19937 g(rd());

            std::shuffle(vec.begin(), vec.end(), g);
        }

    protected:
        int compute_heuristic(const State &ancestorState) override;
        void compute_post_hoc() override;

    public:
        explicit LocalSearch(const plugins::Options &opts);
        virtual ~LocalSearch() = default;
    };
}

#endif
