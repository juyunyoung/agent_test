sql_examples = [
    {
        "input": "충청남도프로젝트1 의 프로젝트 기본 테이블에서 프로젝트 정보를 검색해 주세요", 
        "answer": """
                  SELECT * 
                    FROM `corded-forge-433107-v9.PROJECTCONT.project_basic_info` 
                    WHERE project_name = '충청남도프로젝트1'
                    """   
    },
    {
        "input": "강원도에서 진행중인 프로젝트의 시작일과 종료일을 가르쳐 주세요?", 
        "answer": """
              SELECT 
                project_name,
                project_code,
                project_start_date,
                project_end_date
              FROM 
                `corded-forge-433107-v9.PROJECTCONT.project_basic_info`
              WHERE 
                address LIKE '%강원도%'
"""
    },
    {
        "input": "강원도프로젝트1의 영업 담당 정보를 가르쳐 주세요", 
        "answer": """
            SELECT distinct pmi.*
            FROM `corded-forge-433107-v9.PROJECTCONT.project_basic_info` AS pbi
            JOIN `corded-forge-433107-v9.PROJECTCONT.project_contract_info` AS pci 
              ON pbi.project_code = pci.project_code
            JOIN `corded-forge-433107-v9.PROJECTCONT.project_contract_member` AS pcm
              ON pbi.project_code = pcm.project_code
            JOIN `corded-forge-433107-v9.PROJECTCONT.project_manager_info` AS pmi
              ON pcm.business_manager = pmi.name
            WHERE pbi.project_name = '강원도프로젝트1';
"""
    },
    {
        "input": "경상북도프로젝트2과 계약된 업체의 정보를 가르쳐 주세요", 
        "answer": """
                    SELECT
                    pci.project_code,
                    pci.partner_name,
                    pci.partner_code,
                    pci.contract_amount,
                    pci.contract_condition,
                    pci.contract_manager,
                    pci.contract_start_date,
                    pci.contract_signing_date,
                    pci.contract_end_data,
                    pbi.project_name
                  FROM
                    `corded-forge-433107-v9.PROJECTCONT.project_basic_info` as pbi,
                  `corded-forge-433107-v9.PROJECTCONT.project_contract_info` as pci
                  where
                    pbi.project_code = pci.project_code
                  and  pbi.project_name ="경상북도프로젝트2";
                """
    },
]