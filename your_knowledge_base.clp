
    (deftemplate job
        (slot title)
        (multislot required_skills)
        (multislot desired_skills)
        (slot required_degree)
    )

    (deftemplate candidate
        (slot name)
        (multislot skills)
        (slot degree)
    )

    (defrule qualified
        (job (title ?jt) (required_skills $?req_skills) (desired_skills $?des_skills) (required_degree ?req_deg))
        (candidate (name ?cn) (skills $?cand_skills) (degree ?deg&:(eq ?deg ?req_deg)))
        (test (subsetp $?req_skills $?cand_skills)) ; Ensure all required skills are present
        =>
        (bind ?match_count 0)
        (foreach ?skill ?des_skills
            (if (member$ ?skill ?cand_skills) then 
                (bind ?match_count (+ ?match_count 1))
                (printout t ?cn " matches the desired skill: " ?skill crlf)
            )
        )
        (printout t ?cn " is qualified for the " ?jt " position.")
        (if (> ?match_count 0) then 
            (printout t " (Preferred: Matches " ?match_count " desired skills)")
        )
        (printout t crlf))
    